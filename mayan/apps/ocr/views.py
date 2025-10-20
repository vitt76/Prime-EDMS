from django.contrib import messages
from django.http import HttpResponseRedirect
from django.urls import reverse, reverse_lazy
from django.utils.translation import ugettext_lazy as _, ungettext

from mayan.apps.documents.forms.document_type_forms import DocumentTypeFilteredSelectForm
from mayan.apps.documents.models.document_models import Document
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.models.document_version_models import DocumentVersion
from mayan.apps.documents.models.document_version_page_models import DocumentVersionPage
from mayan.apps.views.generics import (
    FormView, MultipleObjectConfirmActionView, MultipleObjectDeleteView,
    SingleObjectDetailView, SingleObjectDownloadView, SingleObjectEditView
)
from mayan.apps.views.mixins import ExternalObjectViewMixin

from .forms import (
    DocumentVersionPageOCRContentDetailForm,
    DocumentVersionPageOCRContentEditForm, DocumentVersionOCRContentForm
)
from .icons import (
    icon_document_type_ocr_settings, icon_document_type_ocr_submit,
    icon_document_version_ocr_content_single_delete,
    icon_document_version_ocr_content_detail,
    icon_document_version_ocr_content_download,
    icon_document_version_ocr_single_submit,
    icon_document_version_page_ocr_content_detail,
    icon_document_version_page_ocr_content_edit
)
from .models import DocumentVersionPageOCRContent
from .permissions import (
    permission_document_version_ocr_content_edit,
    permission_document_version_ocr_content_view,
    permission_document_version_ocr, permission_document_type_ocr_setup
)


class DocumentTypeOCRSettingsEditView(
    ExternalObjectViewMixin, SingleObjectEditView
):
    external_object_class = DocumentType
    external_object_permission = permission_document_type_ocr_setup
    external_object_pk_url_kwarg = 'document_type_id'
    fields = ('auto_ocr',)
    post_action_redirect = reverse_lazy(
        viewname='documents:document_type_list'
    )
    view_icon = icon_document_type_ocr_settings

    def get_document_type(self):
        return self.external_object

    def get_extra_context(self):
        return {
            'object': self.get_document_type(),
            'title': _(
                'Edit OCR settings for document type: %s.'
            ) % self.get_document_type()
        }

    def get_object(self, queryset=None):
        return self.get_document_type().ocr_settings


class DocumentTypeOCRSubmitView(FormView):
    extra_context = {
        'title': _('Submit all documents of a type for OCR')
    }
    form_class = DocumentTypeFilteredSelectForm
    post_action_redirect = reverse_lazy(viewname='common:tools_list')
    view_icon = icon_document_type_ocr_submit

    def form_valid(self, form):
        count = 0

        valid_documents_queryset = Document.valid.all()

        for document_type in form.cleaned_data['document_type']:
            for document in document_type.documents.filter(pk__in=valid_documents_queryset.values('pk')):
                document.submit_for_ocr(_user=self.request.user)
                count += 1

        messages.success(
            message=_(
                '%(count)d documents added to the OCR queue.'
            ) % {
                'count': count,
            }, request=self.request
        )

        return HttpResponseRedirect(redirect_to=self.get_success_url())

    def get_form_extra_kwargs(self):
        return {
            'allow_multiple': True,
            'permission': permission_document_version_ocr,
            'user': self.request.user
        }

    def get_post_action_redirect(self):
        return reverse(viewname='common:tools_list')


class DocumentVersionOCRContentDeleteView(MultipleObjectDeleteView):
    error_message = _(
        'Error deleting document version OCR "%(instance)s"; %(exception)s'
    )
    object_permission = permission_document_version_ocr
    pk_url_kwarg = 'document_version_id'
    source_queryset = DocumentVersion.valid.all()
    success_message_single = _(
        'OCR content of "%(object)s" deleted successfully.'
    )
    success_message_singular = _(
        'OCR content of %(count)d document version deleted successfully.'
    )
    success_message_plural = _(
        'OCR content of %(count)d document versions deleted successfully.'
    )
    title_single = _('Delete the OCR content of: %(object)s.')
    title_singular = _(
        'Delete the OCR content of the %(count)d selected document version.'
    )
    title_plural = _(
        'Delete the OCR content of the %(count)d selected document versions.'
    )
    view_icon = icon_document_version_ocr_content_single_delete

    def object_action(self, form, instance):
        DocumentVersionPageOCRContent.objects.delete_content_for(
            document_version=instance, user=self.request.user
        )


class DocumentVersionOCRContentView(SingleObjectDetailView):
    form_class = DocumentVersionOCRContentForm
    object_permission = permission_document_version_ocr_content_view
    pk_url_kwarg = 'document_version_id'
    source_queryset = DocumentVersion.valid.all()
    view_icon = icon_document_version_ocr_content_detail

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(
            request, *args, **kwargs
        )
        self.object.document.add_as_recent_document_for_user(
            user=request.user
        )
        return result

    def get_extra_context(self):
        return {
            'document': self.object,
            'hide_labels': True,
            'object': self.object,
            'title': _('OCR result for document: %s') % self.object,
        }


class DocumentVersionOCRDownloadView(SingleObjectDownloadView):
    object_permission = permission_document_version_ocr_content_view
    pk_url_kwarg = 'document_version_id'
    source_queryset = DocumentVersion.valid.all()
    view_icon = icon_document_version_ocr_content_download

    def get_download_file_object(self):
        return self.object.ocr_content()

    def get_download_filename(self):
        return '{}-OCR'.format(self.object)


class DocumentVersionOCRSubmitView(MultipleObjectConfirmActionView):
    object_permission = permission_document_version_ocr
    pk_url_kwarg = 'document_version_id'
    source_queryset = DocumentVersion.valid.all()
    success_message = _(
        '%(count)d document version submitted to the OCR queue.'
    )
    success_message_plural = _(
        '%(count)d document versions submitted to the OCR queue.'
    )
    view_icon = icon_document_version_ocr_single_submit

    def get_extra_context(self):
        queryset = self.object_list

        result = {
            'title': ungettext(
                singular='Submit the selected document version to the OCR queue?',
                plural='Submit the selected document versions to the OCR queue?',
                number=queryset.count()
            )
        }

        if queryset.count() == 1:
            result['object'] = queryset.first()

        return result

    def object_action(self, form, instance):
        instance.submit_for_ocr(_user=self.request.user)


class DocumentVersionPageOCRContentDetailView(SingleObjectDetailView):
    form_class = DocumentVersionPageOCRContentDetailForm
    object_permission = permission_document_version_ocr_content_view
    pk_url_kwarg = 'document_version_page_id'
    source_queryset = DocumentVersionPage.valid.all()
    view_icon = icon_document_version_page_ocr_content_detail

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(
            request, *args, **kwargs
        )
        self.object.document_version.document.add_as_recent_document_for_user(
            user=request.user
        )
        return result

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'object': self.object,
            'title': _(
                'OCR result for document version page: %s'
            ) % self.object
        }


class DocumentVersionPageOCRContentEditView(
    ExternalObjectViewMixin, SingleObjectEditView
):
    external_object_queryset = DocumentVersionPage.valid.all()
    external_object_permission = permission_document_version_ocr_content_edit
    external_object_pk_url_kwarg = 'document_version_page_id'
    form_class = DocumentVersionPageOCRContentEditForm
    view_icon = icon_document_version_page_ocr_content_edit

    def dispatch(self, request, *args, **kwargs):
        result = super().dispatch(
            request, *args, **kwargs
        )
        self.external_object.document_version.document.add_as_recent_document_for_user(
            user=request.user
        )
        return result

    def get_extra_context(self):
        return {
            'hide_labels': True,
            'object': self.external_object,
            'title': _(
                'Edit OCR for document version page: %s'
            ) % self.external_object
        }

    def get_instance_extra_data(self):
        return {
            '_event_actor': self.request.user
        }

    def get_object(self):
        try:
            return self.external_object.ocr_content
        except DocumentVersionPageOCRContent.DoesNotExist:
            return DocumentVersionPageOCRContent(
                document_version_page=self.external_object
            )
