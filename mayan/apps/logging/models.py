from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.db import models
from django.utils.translation import ugettext_lazy as _

from mayan.apps.events.classes import EventManagerMethodAfter
from mayan.apps.events.decorators import method_event

from .classes import ErrorLog as ErrorLogProxy
from .events import event_error_log_deleted
from .managers import ErrorLogPartitionEntryManager


class StoredErrorLog(models.Model):
    name = models.CharField(
        max_length=128, unique=True, verbose_name=_('Internal name')
    )

    class Meta:
        ordering = ('name',)
        verbose_name = _('Error log')
        verbose_name_plural = _('Error logs')

    def __str__(self):
        return str(self.app_label)

    @property
    def app_label(self):
        return self.proxy.app_config

    app_label.fget.short_description = _('App label')

    @property
    def proxy(self):
        return ErrorLogProxy.get(name=self.name)


class ErrorLogPartition(models.Model):
    error_log = models.ForeignKey(
        on_delete=models.CASCADE, related_name='partitions',
        to=StoredErrorLog, verbose_name=_('Error log')
    )
    name = models.CharField(
        db_index=True, max_length=128, verbose_name=_('Internal name')
    )
    content_type = models.ForeignKey(
        on_delete=models.CASCADE, to=ContentType
    )
    object_id = models.PositiveIntegerField()
    content_object = GenericForeignKey(
        ct_field='content_type', fk_field='object_id'
    )

    class Meta:
        unique_together = (
            ('error_log', 'name'), ('error_log', 'content_type', 'object_id')
        )
        verbose_name = _('Error log partition')
        verbose_name_plural = _('Error log partitions')

    def __str__(self):
        return self.name


class ErrorLogPartitionEntry(models.Model):
    error_log_partition = models.ForeignKey(
        on_delete=models.CASCADE, related_name='entries',
        to=ErrorLogPartition, verbose_name=_('Error log partition')
    )
    datetime = models.DateTimeField(
        auto_now_add=True, db_index=True, verbose_name=_('Date and time')
    )
    text = models.TextField(blank=True, null=True, verbose_name=_('Text'))

    objects = ErrorLogPartitionEntryManager()

    class Meta:
        get_latest_by = 'datetime'
        ordering = ('datetime',)
        verbose_name = _('Error log partition entry')
        verbose_name_plural = _('Error log partition entries')

    def __str__(self):
        return '{} {}'.format(self.datetime, self.text)

    @method_event(
        event_manager_class=EventManagerMethodAfter,
        event=event_error_log_deleted,
        target='error_log_partition.content_object'
    )
    def delete(self, *args, **kwargs):
        return super().delete(*args, **kwargs)

    def get_object(self):
        return self.error_log_partition.content_object

    get_object.short_description = _('Object')


class GlobalErrorLogPartitionEntry(ErrorLogPartitionEntry):
    class Meta:
        proxy = True
