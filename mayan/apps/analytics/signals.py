from django.contrib.auth.signals import user_logged_in, user_logged_out
from django.dispatch import receiver
from django.utils import timezone

from .models import UserSession


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


