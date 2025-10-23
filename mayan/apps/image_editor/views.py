from django.contrib import messages
from django.http import HttpResponse, JsonResponse
from django.utils.translation import ugettext_lazy as _
from django.views.generic import TemplateView, View

from mayan.apps.documents.document_file_actions import DocumentFileActionUseNewPages
from mayan.apps.documents.models.document_file_models import DocumentFile
from mayan.apps.documents.permissions import permission_document_file_edit
from mayan.apps.views.generics import SingleObjectDetailView
from mayan.apps.views.mixins import ExternalObjectViewMixin

from .forms import ImageEditorSaveForm
from .permissions import permission_image_edit


class ImageEditorView(SingleObjectDetailView):
    """Отображение редактора для выбранного файла документа."""

    fields = ()  # Empty fields for DetailView (no form needed)
    model = DocumentFile
    object_permission = permission_image_edit
    pk_url_kwarg = 'document_file_id'
    template_name = 'image_editor/editor.html'

    def get_extra_context(self):
        # Временно упрощенная версия для отладки
        print("=== ImageEditorView.get_extra_context called ===")
        print(f"object: {self.object}")
        print(f"object.pk: {self.object.pk if self.object else None}")

        if not self.object:
            print("ERROR: Object not found")
            return {
                'document_file': None,
                'document': None,
                'title': 'Ошибка: файл не найден',
            }

        print("SUCCESS: Object found, returning context")
        return {
            'document_file': self.object,
            'document': self.object.document,
            'title': f'Редактирование изображения: {self.object.filename}',
        }


class ImageEditorSaveView(ExternalObjectViewMixin, View):
    """Сохранение изменений изображения и создание новой версии."""

    external_object_permission = permission_document_file_edit
    external_object_pk_url_kwarg = 'document_file_id'
    external_object_queryset = DocumentFile.objects.all()

    def post(self, request, *args, **kwargs):
        document_file = self.external_object

        form = ImageEditorSaveForm(data=request.POST, files=request.FILES)
        if not form.is_valid():
            return JsonResponse({'success': False, 'errors': form.errors}, status=400)

        image_file = form.cleaned_data['image_content']
        action_id = form.cleaned_data['action_id'] or DocumentFileActionUseNewPages.backend_id
        comment = form.cleaned_data.get('comment') or _('Редактирование изображения через редактор')
        target_format = form.cleaned_data.get('format', 'jpeg').upper()

        # Конвертируем изображение в выбранный формат
        try:
            from PIL import Image
            import io

            # Открываем изображение
            image = Image.open(image_file)
            print(f"Original image format: {image.format}, mode: {image.mode}")

            # Конвертируем в нужный формат
            output_buffer = io.BytesIO()
            if target_format == 'PNG':
                image.save(output_buffer, format='PNG')
                content_type = 'image/png'
                file_extension = 'png'
            elif target_format == 'WEBP':
                image.save(output_buffer, format='WebP')
                content_type = 'image/webp'
                file_extension = 'webp'
            elif target_format == 'TIFF':
                image.save(output_buffer, format='TIFF')
                content_type = 'image/tiff'
                file_extension = 'tiff'
            else:
                # По умолчанию JPEG
                image.save(output_buffer, format='JPEG')
                content_type = 'image/jpeg'
                file_extension = 'jpeg'

            print(f"Converted to {target_format}, buffer size: {output_buffer.tell()}")

            # Создаем новый файл с конвертированным изображением
            output_buffer.seek(0)
            from django.core.files.base import ContentFile
            converted_file = ContentFile(output_buffer.getvalue(), name=f'converted.{file_extension}')

            new_document_file = document_file.document.file_new(
                file_object=converted_file,
                action=action_id,
                comment=f'{comment} (конвертировано в {target_format})',
                filename=document_file.filename,
                _user=request.user
            )

            print(f"New document file created with ID: {new_document_file.pk}")

        except Exception as e:
            print(f"Conversion error: {str(e)}")
            import traceback
            traceback.print_exc()
            return JsonResponse({'success': False, 'errors': {'conversion': f'Ошибка конвертации: {str(e)}'}}, status=500)

        return JsonResponse({'success': True, 'document_file_id': new_document_file.pk})
