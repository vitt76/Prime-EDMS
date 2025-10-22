from django.db import models
from django.utils.translation import ugettext_lazy as _


class ImageEditSession(models.Model):
    """Сессия редактирования изображения."""

    STATUS_CHOICES = (
        ('editing', _('Редактируется')),
        ('saved', _('Сохранено')),
        ('cancelled', _('Отменено')),
    )

    document_file = models.ForeignKey(
        'documents.DocumentFile',
        on_delete=models.CASCADE,
        related_name='image_edit_sessions',
        verbose_name=_('Файл документа')
    )
    user = models.ForeignKey(
        'auth.User',
        on_delete=models.CASCADE,
        related_name='image_edit_sessions',
        verbose_name=_('Пользователь')
    )
    original_checksum = models.CharField(
        blank=True,
        max_length=64,
        verbose_name=_('Исходный checksum')
    )
    edited_checksum = models.CharField(
        blank=True,
        max_length=64,
        verbose_name=_('Checksum после редактирования')
    )
    status = models.CharField(
        choices=STATUS_CHOICES,
        default='editing',
        max_length=32,
        verbose_name=_('Статус')
    )
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))
    modified = models.DateTimeField(auto_now=True, verbose_name=_('Изменено'))

    class Meta:
        verbose_name = _('Сессия редактирования изображения')
        verbose_name_plural = _('Сессии редактирования изображений')

    def __str__(self):
        return f'{self.document_file} ({self.status})'


class ImageEditOperation(models.Model):
    """Отдельная операция редактирования в рамках сессии."""

    OPERATION_TYPE_CHOICES = (
        ('crop', _('Обрезка')),
        ('rotate', _('Поворот')),
        ('flip', _('Отражение')),
        ('brightness', _('Яркость')),
        ('contrast', _('Контраст')),
        ('draw', _('Рисование')),
        ('text', _('Текст')),
        ('filter', _('Фильтр')),
    )

    session = models.ForeignKey(
        ImageEditSession,
        on_delete=models.CASCADE,
        related_name='operations',
        verbose_name=_('Сессия')
    )
    operation_type = models.CharField(
        choices=OPERATION_TYPE_CHOICES,
        max_length=32,
        verbose_name=_('Тип операции')
    )
    parameters = models.JSONField(verbose_name=_('Параметры операции'))
    order = models.PositiveIntegerField(verbose_name=_('Порядок'))
    created = models.DateTimeField(auto_now_add=True, verbose_name=_('Создано'))

    class Meta:
        ordering = ('order', 'created')
        verbose_name = _('Операция редактирования изображения')
        verbose_name_plural = _('Операции редактирования изображения')

    def __str__(self):
        return f'{self.operation_type} ({self.order})'
