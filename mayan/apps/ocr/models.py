from django.db import models
from django.utils.encoding import force_text
from django.utils.translation import ugettext_lazy as _

from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.documents.models.document_type_models import DocumentType
from mayan.apps.documents.models.document_version_page_models import DocumentVersionPage
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event

from .events import event_ocr_document_version_page_content_edited
from .managers import (
    DocumentVersionPageOCRContentManager, DocumentTypeSettingsManager
)


class DocumentTypeOCRSettings(ExtraDataModelMixin, models.Model):
    """
    Model to store the OCR settings for a document type.
    """
    document_type = models.OneToOneField(
        on_delete=models.CASCADE, related_name='ocr_settings',
        to=DocumentType, unique=True, verbose_name=_('Document type')
    )
    auto_ocr = models.BooleanField(
        default=True,
        verbose_name=_('Automatically queue newly created documents for OCR.')
    )

    objects = DocumentTypeSettingsManager()

    class Meta:
        verbose_name = _('Document type settings')
        verbose_name_plural = _('Document types settings')

    def natural_key(self):
        return self.document_type.natural_key()
    natural_key.dependencies = ['documents.DocumentType']


class DocumentVersionPageOCRContent(models.Model):
    """
    This model stores the OCR results for a document version page.
    """
    document_version_page = models.OneToOneField(
        on_delete=models.CASCADE, related_name='ocr_content',
        to=DocumentVersionPage, verbose_name=_('Document version page')
    )
    content = models.TextField(
        blank=True, help_text=_(
            'The actual text content extracted by the OCR backend.'
        ), verbose_name=_('Content')
    )

    objects = DocumentVersionPageOCRContentManager()

    class Meta:
        verbose_name = _('Document version page OCR content')
        verbose_name_plural = _('Document version pages OCR contents')

    def __str__(self):
        return force_text(s=self.document_version_page)

    @method_event(
        event_manager_class=EventManagerSave,
        edited={
            'action_object': 'document_version_page.document_version.document',
            'event': event_ocr_document_version_page_content_edited,
            'target': 'document_version_page'
        }
    )
    def save(self, *args, **kwargs):
        return super().save(*args, **kwargs)
