import logging
from pathlib import Path
import uuid

from django.apps import apps
from django.core.files import File
from django.db import models, transaction
from django.urls import reverse
from django.utils.timezone import now
from django.utils.translation import ugettext, ugettext_lazy as _

from mayan.apps.converter.exceptions import AppImageError
from mayan.apps.databases.model_mixins import ExtraDataModelMixin
from mayan.apps.common.signals import signal_mayan_pre_save
from mayan.apps.events.classes import EventManagerSave
from mayan.apps.events.decorators import method_event
from mayan.apps.storage.compressed_files import Archive
from mayan.apps.storage.exceptions import NoMIMETypeMatch

from ..classes import DocumentFileAction
from ..document_file_actions import DocumentFileActionUseNewPages
from ..events import (
    event_document_created, event_document_edited,
    event_document_trashed, event_document_type_changed,
    event_trashed_document_deleted
)
from ..literals import DEFAULT_LANGUAGE, IMAGE_ERROR_NO_ACTIVE_VERSION
from ..managers import (
    DocumentManager, TrashCanManager, ValidDocumentManager,
    ValidRecentlyCreatedDocumentManager
)
from ..signals import signal_post_document_type_change

from .document_type_models import DocumentType
from .mixins import HooksModelMixin

__all__ = ('Document', 'DocumentSearchResult',)
logger = logging.getLogger(name=__name__)


class Document(
    ExtraDataModelMixin, HooksModelMixin, models.Model
):
    """
    Defines a single document with it's fields and properties
    Fields:
    * uuid - UUID of a document, universally Unique ID. An unique identifier
    generated for each document. No two documents can ever have the same UUID.
    This ID is generated automatically.
    """
    _hooks_pre_create = []

    uuid = models.UUIDField(
        default=uuid.uuid4, editable=False, help_text=_(
            'UUID of a document, universally Unique ID. An unique identifier '
            'generated for each document.'
        ), verbose_name=_('UUID')
    )
    document_type = models.ForeignKey(
        help_text=_('The document type of the document.'),
        on_delete=models.CASCADE, related_name='documents', to=DocumentType,
        verbose_name=_('Document type')
    )
    label = models.CharField(
        blank=True, db_index=True, default='', max_length=255,
        help_text=_(
            'A short text identifying the document. By default, will be '
            'set to the filename of the first file uploaded to the document.'
        ),
        verbose_name=_('Label')
    )
    description = models.TextField(
        blank=True, default='', help_text=_(
            'An optional short text describing a document.'
        ), verbose_name=_('Description')
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True, db_index=True, help_text=_(
            'The date and time of the document creation.'
        ), verbose_name=_('Created')
    )
    language = models.CharField(
        blank=True, default=DEFAULT_LANGUAGE, help_text=_(
            'The primary language in the document.'
        ), max_length=8, verbose_name=_('Language')
    )
    in_trash = models.BooleanField(
        db_index=True, default=False, help_text=_(
            'Whether or not this document is in the trash.'
        ), editable=False, verbose_name=_('In trash?')
    )
    trashed_date_time = models.DateTimeField(
        blank=True, editable=True, help_text=_(
            'The server date and time when the document was moved to the '
            'trash.'
        ), null=True, verbose_name=_('Date and time trashed')
    )
    is_stub = models.BooleanField(
        db_index=True, default=True, editable=False, help_text=_(
            'A document stub is a document with an entry on the database but '
            'no file uploaded. This could be an interrupted upload or a '
            'deferred upload via the API.'
        ), verbose_name=_('Is stub?')
    )

    objects = DocumentManager()
    trash = TrashCanManager()
    valid = ValidDocumentManager()

    @classmethod
    def execute_pre_create_hooks(cls, kwargs=None):
        """
        Helper method to allow checking if it is possible to create
        a new document.
        """
        cls._execute_hooks(
            hook_list=cls._hooks_pre_create, kwargs=kwargs
        )

    @classmethod
    def register_pre_create_hook(cls, func, order=None):
        cls._insert_hook_entry(
            hook_list=cls._hooks_pre_create, func=func, order=order
        )

    class Meta:
        ordering = ('label',)
        verbose_name = _('Document')
        verbose_name_plural = _('Documents')

    def __str__(self):
        return self.get_label()

    def add_as_recent_document_for_user(self, user):
        RecentlyAccessedDocument = apps.get_model(
            app_label='documents', model_name='RecentlyAccessedDocument'
        )
        return RecentlyAccessedDocument.valid.add_document_for_user(
            document=self, user=user
        )

    def delete(self, *args, **kwargs):
        to_trash = kwargs.pop('to_trash', True)
        user = kwargs.pop('_user', self.__dict__.pop('_event_actor', None))

        if not self.in_trash and to_trash:
            self.in_trash = True
            self.trashed_date_time = now()
            with transaction.atomic():
                self._event_ignore = True
                self.save(update_fields=('in_trash', 'trashed_date_time'))

            event_document_trashed.commit(actor=user, target=self)
        else:
            with transaction.atomic():
                for document_file in self.files.all():
                    document_file.delete()

                super().delete(*args, **kwargs)

            event_trashed_document_deleted.commit(
                actor=user, target=self.document_type
            )

    def document_type_change(self, document_type, force=False, _user=None):
        has_changed = self.document_type != document_type

        if has_changed or force:
            self.document_type = document_type

            self._event_ignore = True
            self.save(update_fields=('document_type',))

            if _user:
                self.add_as_recent_document_for_user(user=_user)

            signal_post_document_type_change.send(
                sender=self.__class__, instance=self
            )

            event_document_type_changed.commit(
                action_object=document_type, actor=_user, target=self
            )

    @property
    def file_latest(self):
        return self.files.order_by('timestamp').last()

    def file_new(
        self, file_object, action=None, comment=None, filename=None,
        expand=False, _user=None
    ):
        logger.info('Creating new document file for document: %s', self)

        if not action:
            action = DocumentFileActionUseNewPages.backend_id

        if not comment:
            comment = ''

        DocumentFile = apps.get_model(
            app_label='documents', model_name='DocumentFile'
        )

        if expand:
            try:
                compressed_file = Archive.open(file_object=file_object)
                for compressed_file_member in compressed_file.members():
                    with compressed_file.open_member(filename=compressed_file_member) as compressed_file_member_file_object:
                        # Recursive call to expand nested compressed files
                        # expand=True literal for recursive nested files.
                        # Might cause problem with office files inside a
                        # compressed file.
                        # Don't use keyword arguments for Path to allow
                        # partials.
                        self.file_new(
                            action=action, comment=comment, expand=False,
                            file_object=compressed_file_member_file_object,
                            filename=Path(compressed_file_member).name,
                            _user=_user
                        )

                # Avoid executing the expand=False code path.
                return
            except NoMIMETypeMatch:
                logger.debug(msg='No expanding; Exception: NoMIMETypeMatch')
                # Fall through to same code path as expand=False to avoid
                # duplicating code.

        try:
            document_file = DocumentFile(
                document=self, comment=comment, file=File(file=file_object),
                filename=filename or Path(file_object.name).name
            )
            document_file._event_actor = _user
            document_file.save()
        except Exception as exception:
            logger.error(
                'Error creating new file for document: %s; %s', self,
                exception, exc_info=True
            )
            raise
        else:
            logger.info('New document file queued for document: %s', self)

            DocumentFileAction.get(name=action).execute(
                document=self, document_file=document_file, comment=comment,
                _user=_user
            )

            return document_file

    def get_absolute_url(self):
        return reverse(
            viewname='documents:document_preview', kwargs={
                'document_id': self.pk
            }
        )

    def get_api_image_url(self, *args, **kwargs):
        version_active = self.version_active
        if version_active:
            return version_active.get_api_image_url(*args, **kwargs)
        else:
            raise AppImageError(error_name=IMAGE_ERROR_NO_ACTIVE_VERSION)

    def get_label(self):
        return self.label or ugettext('Document stub, id: %d') % self.pk

    get_label.short_description = _('Label')

    @property
    def is_in_trash(self):
        return self.in_trash

    def natural_key(self):
        return (self.uuid,)
    natural_key.dependencies = ['documents.DocumentType']

    @property
    def pages(self):
        try:
            return self.version_active.pages
        except AttributeError:
            # Document has no version yet.
            DocumentVersionPage = apps.get_model(
                app_label='documents', model_name='DocumentVersionPage'
            )

            return DocumentVersionPage.objects.none()

    @method_event(
        event_manager_class=EventManagerSave,
        created={
            'event': event_document_created,
            'action_object': 'document_type',
            'target': 'self'
        },
        edited={
            'event': event_document_edited,
            'target': 'self'
        }
    )
    def save(self, *args, **kwargs):
        user = self.__dict__.pop('_event_actor', None)
        new_document = not self.pk

        signal_mayan_pre_save.send(
            sender=Document, instance=self, user=user
        )

        super().save(*args, **kwargs)

        if new_document:
            if user:
                self.add_as_recent_document_for_user(user=user)

    @property
    def version_active(self):
        try:
            return self.versions.filter(active=True).first()
        except self.versions.model.DoesNotExist:
            return self.versions.none()


class DocumentSearchResult(Document):
    class Meta:
        proxy = True


class RecentlyCreatedDocument(Document):
    objects = models.Manager()
    valid = ValidRecentlyCreatedDocumentManager()

    class Meta:
        proxy = True
