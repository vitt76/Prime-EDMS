from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone

from .models import ApprovalWorkflowEvent, UserSession


@receiver(signal=user_logged_in)
def handler_user_logged_in(sender, request, user, **kwargs):
    """Track user logins as analytics sessions (Level 3)."""
    session_key = ''
    ip_address = None
    user_agent = ''

    try:
        session_key = request.session.session_key or ''
    except Exception:
        session_key = ''

    try:
        ip_address = request.META.get('REMOTE_ADDR')
    except Exception:
        ip_address = None

    try:
        user_agent = request.META.get('HTTP_USER_AGENT', '') or ''
    except Exception:
        user_agent = ''

    UserSession.objects.create(
        user=user,
        session_key=session_key,
        login_timestamp=timezone.now(),
        ip_address=ip_address,
        user_agent=user_agent,
    )


@receiver(signal=user_logged_out)
def handler_user_logged_out(sender, request, user, **kwargs):
    """Close the latest open analytics session on logout (best-effort)."""
    session_key = ''

    try:
        session_key = request.session.session_key or ''
    except Exception:
        session_key = ''

    qs = UserSession.objects.filter(
        user=user, logout_timestamp__isnull=True
    ).order_by('-login_timestamp')

    if session_key:
        qs = qs.filter(session_key=session_key)

    session = qs.first()
    if not session:
        return

    now = timezone.now()
    session.logout_timestamp = now
    session.session_duration_seconds = int((now - session.login_timestamp).total_seconds())
    session.save(update_fields=('logout_timestamp', 'session_duration_seconds'))


@receiver(signal=post_save)
def handler_document_file_upload(sender, instance, created, **kwargs):
    """Track document file uploads as analytics asset upload events (Level 1).

    This handler listens to post_save for DocumentFile and records an
    AssetEvent(EVENT_TYPE_UPLOAD). This is best-effort and should never break
    the upload flow.
    """
    try:
        from mayan.apps.documents.models import DocumentFile
    except Exception:
        return

    if sender is not DocumentFile:
        return
    if not created:
        return

    try:
        from .models import AssetEvent
        from .utils import track_asset_event

        user = getattr(instance, '_event_actor', None)
        # Some upload flows might not attach _event_actor; keep best-effort.
        if user is not None and getattr(user, 'is_authenticated', True) is False:
            user = None

        track_asset_event(
            document=instance.document,
            event_type=AssetEvent.EVENT_TYPE_UPLOAD,
            user=user,
            channel='dam_interface',
            metadata={
                'document_file_id': instance.pk,
                'mimetype': instance.mimetype,
                'size': instance.size,
            }
        )
    except Exception:
        # Never break uploads due to analytics issues.
        return


@receiver(signal=post_save)
def handler_workflow_instance_log_entry(sender, instance, created, **kwargs):
    """Track approval workflow transitions via WorkflowInstanceLogEntry.

    This is heuristic-based because workflow transition names/labels can be
    customized per deployment. We interpret common transition names:
    - submit / send / review -> submission
    - approve -> approved
    - reject -> rejected

    The tracker creates a new ApprovalWorkflowEvent on submission and updates
    the last pending event on approve/reject.
    """
    try:
        from mayan.apps.document_states.models import WorkflowInstanceLogEntry
    except Exception:
        return

    if sender is not WorkflowInstanceLogEntry:
        return
    if not created:
        return

    try:
        transition = instance.transition
        name = (getattr(transition, 'name', '') or '').lower()
        label = (getattr(transition, 'label', '') or '').lower()
        dst_label = (getattr(getattr(transition, 'destination_state', None), 'label', '') or '').lower()

        text = ' '.join([name, label, dst_label])
        is_submit = any(k in text for k in ('submit', 'send', 'review', 'pending'))
        is_approve = any(k in text for k in ('approve', 'approved', 'accept'))
        is_reject = any(k in text for k in ('reject', 'rejected', 'decline'))

        # If multiple match, prefer approve/reject.
        if is_approve:
            event_type = 'approve'
        elif is_reject:
            event_type = 'reject'
        elif is_submit:
            event_type = 'submit'
        else:
            return

        workflow_instance = instance.workflow_instance
        document = workflow_instance.document
        user = instance.user
        timestamp = instance.datetime

        if event_type == 'submit':
            last_attempt = (
                ApprovalWorkflowEvent.objects.filter(
                    workflow_instance=workflow_instance, document=document
                ).order_by('-submitted_at').first()
            )
            attempt = 1
            if last_attempt:
                attempt = int(last_attempt.attempt_number or 1) + 1

            ApprovalWorkflowEvent.objects.create(
                document=document,
                workflow_instance=workflow_instance,
                submitter=user,
                submitted_at=timestamp,
                status=ApprovalWorkflowEvent.STATUS_PENDING,
                attempt_number=attempt,
            )
            return

        pending = ApprovalWorkflowEvent.objects.filter(
            workflow_instance=workflow_instance,
            document=document,
            status=ApprovalWorkflowEvent.STATUS_PENDING,
        ).order_by('-submitted_at').first()

        # If no pending record exists (e.g., started midstream), create one.
        if not pending:
            pending = ApprovalWorkflowEvent.objects.create(
                document=document,
                workflow_instance=workflow_instance,
                submitter=None,
                submitted_at=timestamp,
                status=ApprovalWorkflowEvent.STATUS_PENDING,
                attempt_number=1,
            )

        if event_type == 'approve':
            pending.approver = user
            pending.approved_at = timestamp
            pending.status = ApprovalWorkflowEvent.STATUS_APPROVED
            delta = pending.approved_at - pending.submitted_at
            pending.approval_time_days = round(delta.total_seconds() / 86400, 4)
            pending.save(update_fields=('approver', 'approved_at', 'status', 'approval_time_days'))
        elif event_type == 'reject':
            pending.approver = user
            pending.rejected_at = timestamp
            pending.status = ApprovalWorkflowEvent.STATUS_REJECTED
            pending.rejection_reason = (instance.comment or '').strip()
            delta = pending.rejected_at - pending.submitted_at
            pending.approval_time_days = round(delta.total_seconds() / 86400, 4)
            pending.save(update_fields=('approver', 'rejected_at', 'status', 'rejection_reason', 'approval_time_days'))
    except Exception:
        return


