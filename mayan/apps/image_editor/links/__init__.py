from django.utils.translation import ugettext_lazy as _

from mayan.apps.navigation.classes import Link

from ..icons import icon_image_editor


def is_image_file(context, resolved_object=None):
    """Проверяет, является ли файл изображением по MIME."""
    document_file = resolved_object or context.get('object')
    if not document_file:
        return False
    mimetype = getattr(document_file, 'mimetype', '') or ''
    return mimetype.startswith('image/')


link_document_file_edit_image = Link(
    icon=icon_image_editor,
    text=_('Изменить изображение'),
    view='image_editor:edit_image',
    args='object.pk',
    condition=is_image_file
)
