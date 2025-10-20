import logging

from django.contrib import messages
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _

from mayan.apps.acls.models import AccessControlList
from mayan.apps.common.settings import setting_home_view
from mayan.apps.views.generics import (
    ConfirmView, MultipleObjectConfirmActionView
)

from ..icons import (
    icon_document_trash_send, icon_trash_can_empty,
    icon_trashed_document_delete, icon_trashed_document_list,
    icon_trashed_document_restore
)
from ..models.document_models import Document
from ..models.trashed_document_models import TrashedDocument
from ..permissions import (
    permission_trashed_document_delete, permission_trashed_document_restore,
    permission_document_trash, permission_document_view,
    permission_trash_empty
)
from ..tasks import task_trashed_document_delete, task_trash_can_empty

from .document_views import DocumentListView

__all__ = (
    'DocumentTrashView', 'EmptyTrashCanView', 'TrashedDocumentDeleteView',
    'TrashedDocumentListView', 'TrashedDocumentRestoreView'
)
logger = logging.getLogger(name=__name__)


class DocumentTrashView(MultipleObjectConfirmActionView):
    object_permission = permission_document_trash
    pk_url_kwarg = 'document_id'
    source_queryset = Document.valid.all()
    success_message_single = _(
        'Document "%(object)s" moved to trash.'
    )
    success_message_singular = _(
        '%(count)d document moved to the trash.'
    )
    success_message_plural = _(
        '%(count)d documents moved to the trash.'
    )
    title_single = _('Move the document "%(object)s" to trash?')
    title_singular = _('Move the selected document to the trash?')
    title_plural = _('Move the %(count)d selected documents to trash?')
    view_icon = icon_document_trash_send

    def get_extra_context(self):
        context = {}

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def get_post_action_redirect(self):
        # Return to the previous view after moving the document to trash
        # unless the move happened from the document view, in which case
        # redirecting back to the document is not possible because it is
        # now a trashed document and not accessible.
        if 'document_id' in self.kwargs:
            return reverse(viewname=setting_home_view.value)
        else:
            return None

    def object_action(self, form, instance):
        instance.delete(_user=self.request.user)


class EmptyTrashCanView(ConfirmView):
    action_cancel_redirect = post_action_redirect = reverse_lazy(
        'documents:document_list_deleted'
    )
    extra_context = {
        'title': _('Empty trash?')
    }
    view_icon = icon_trash_can_empty
    view_permission = permission_trash_empty

    def view_action(self):
        task_trash_can_empty.apply_async(
            kwargs={
                'user_id': self.request.user.pk
            }
        )

        messages.success(
            message=_('The trash emptying task has been queued.'),
            request=self.request
        )


class TrashedDocumentDeleteView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_delete
    pk_url_kwarg = 'document_id'
    success_message_single = _(
        'Trash document "%(object)s" submitted for deletion.'
    )
    success_message_singular = _(
        '%(count)d trashed document submitted for deletion.'
    )
    success_message_plural = _(
        '%(count)d trashed documents submitted for deletion.'
    )
    title_single = _('Delete the trashed document "%(object)s"?')
    title_singular = _('Delete the selected trashed document?')
    title_plural = _('Delete the %(count)d selected trashed documents?')
    view_icon = icon_trashed_document_delete

    def get_extra_context(self):
        context = {}

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def object_action(self, form, instance):
        task_trashed_document_delete.apply_async(
            kwargs={
                'trashed_document_id': instance.pk,
                'user_id': self.request.user.pk
            }
        )


class TrashedDocumentListView(DocumentListView):
    object_permission = None
    view_icon = icon_trashed_document_list

    def get_document_queryset(self):
        return AccessControlList.objects.restrict_queryset(
            permission=permission_document_view,
            queryset=TrashedDocument.trash.all(),
            user=self.request.user
        )

    def get_extra_context(self):
        context = super().get_extra_context()
        context.update(
            {
                'hide_link': True,
                'no_results_icon': icon_trashed_document_list,
                'no_results_text': _(
                    'To avoid loss of data, documents are not deleted '
                    'instantly. First, they are placed in the trash can. '
                    'From here they can be then finally deleted or restored.'
                ),
                'no_results_title': _(
                    'There are no documents in the trash can'
                ),
                'title': _('Documents in trash'),
            }
        )
        return context


class TrashedDocumentRestoreView(MultipleObjectConfirmActionView):
    model = TrashedDocument
    object_permission = permission_trashed_document_restore
    pk_url_kwarg = 'document_id'
    success_message_single = _(
        'Trashed document "%(object)s" restored.'
    )
    success_message_singular = _(
        '%(count)d trashed document restored.'
    )
    success_message_plural = _(
        '%(count)d trashed documents restored.'
    )
    title_single = _('Restore the trashed document: %(object)s')
    title_singular = _('Restore the selected trashed document?')
    title_plural = _('Restore the %(count)d selected trashed documents?')
    view_icon = icon_trashed_document_restore

    def get_extra_context(self):
        context = {}

        if self.object_list.count() == 1:
            context['object'] = self.object_list.first()

        return context

    def object_action(self, form, instance):
        instance._event_actor = self.request.user
        instance.restore()
