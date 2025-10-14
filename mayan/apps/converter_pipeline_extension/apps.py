from pathlib import Path

from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class ConverterPipelineExtensionApp(MayanAppConfig):
    """
    Converter Pipeline Extension - расширенная система конвертеров для Mayan EDMS.
    """
    app_namespace = 'converter_pipeline_extension'
    app_url = 'converter-pipeline'
    has_rest_api = False
    has_static_media = False
    has_tests = True
    name = 'mayan.apps.converter_pipeline_extension'
    verbose_name = _('Converter Pipeline Extension')
    label = 'converter_pipeline_extension'

    def ready(self):
        super().ready()
        print('🔥 Converter Pipeline Extension loaded successfully!')

        # Регистрация URL вручную (автоматическая регистрация MayanAppConfig не работает)
        try:
            self._register_urls()
        except Exception as e:
            print(f'❌ Failed to register URLs: {e}')
            raise

        # Удаляем устаревший фронтенд-скрипт, если он был установлен ранее
        try:
            self._cleanup_legacy_frontend_assets()
        except Exception as e:
            print(f'⚠️ Failed to cleanup legacy frontend assets: {e}')

        # Регистрация backend'а конвертера
        try:
            self._patch_converter_backend()
        except Exception as e:
            print(f'❌ Failed to patch converter backend: {e}')

    def _register_urls(self):
        """Регистрация URL для конвертации"""
        try:
            from django.urls import include, path
            # Используем тот же импорт, что и в MayanAppConfig
            from mayan.urls import urlpatterns as mayan_urlpatterns

            # Импортируем urls только здесь
            from . import urls
            mayan_urlpatterns.append(
                path('converter-pipeline/', include((urls.urlpatterns, 'converter_pipeline_extension')))
            )
            print('✅ URLs registered successfully!')
        except Exception as e:
            print(f'❌ Failed to register URLs: {e}')
            raise

    def _cleanup_legacy_frontend_assets(self):
        """Удалить ранее установленный JS, добавлявший пункт Convert через DOM."""
        try:
            import mayan.apps.appearance as appearance_module
        except ImportError:
            print('⚠️ Appearance module not found; skipping legacy cleanup.')
            return

        appearance_path = Path(appearance_module.__file__).resolve().parent
        base_template_path = appearance_path / 'templates' / 'appearance' / 'base.html'
        legacy_script_tag = '<script src="{% static "appearance/js/converter_extension.js" %}"></script>'

        if base_template_path.exists():
            content = base_template_path.read_text(encoding='utf-8')
            if legacy_script_tag in content:
                base_template_path.write_text(
                    content.replace(f'{legacy_script_tag}\n', '').replace(legacy_script_tag, ''),
                    encoding='utf-8'
                )
                print('🧹 Removed legacy converter_extension.js script tag from appearance/base.html')

        legacy_js_path = appearance_path / 'static' / 'appearance' / 'js' / 'converter_extension.js'
        if legacy_js_path.exists():
            try:
                legacy_js_path.unlink()
                print('🧹 Deleted legacy converter_extension.js file')
            except Exception as exc:
                print(f'⚠️ Failed to delete legacy converter_extension.js: {exc}')


    def _patch_converter_backend(self):
        """Добавить поддержку видео файлов в конвертер Mayan EDMS"""
        print('🔧 Starting converter backend patching...')
        try:
            # Импортировать конвертер Mayan EDMS
            print('📦 Importing Mayan Python converter...')
            from mayan.apps.converter.backends.python import Python
            print('✅ Python converter imported successfully')

            # Сохранить оригинальный метод convert
            original_convert = Python.convert
            print('💾 Original convert method saved')

            def patched_convert(self, *args, **kwargs):
                print(f'🔄 Convert called for MIME type: {self.mime_type}')
                # Вызвать оригинальный метод
                result = original_convert(self, *args, **kwargs)
                print(f'📋 Original convert result: {type(result)}')

                # Если результат None (не поддерживаемый формат), проверить видео
                if result is None and self.mime_type and self.mime_type.startswith('video/'):
                    print(f'🎬 Converting video file with MIME type: {self.mime_type}')
                    try:
                        # Использовать наш VideoConverter
                        print('🎥 Importing VideoConverter...')
                        from .backends.video import VideoConverter
                        print('✅ VideoConverter imported')

                        # Создать экземпляр VideoConverter
                        print('🏗️ Creating VideoConverter instance...')
                        video_converter = VideoConverter(self.file_object)
                        print('✅ VideoConverter instance created')

                        # Получить preview
                        print('🎬 Generating video preview...')
                        preview_content = video_converter.convert_to_preview()
                        print(f'📸 Preview content generated: {type(preview_content)}')

                        if preview_content:
                            # Конвертировать ContentFile в PIL Image
                            print('🖼️ Converting to PIL Image...')
                            from PIL import Image
                            from io import BytesIO

                            preview_data = BytesIO(preview_content.read())
                            result = Image.open(preview_data)
                            print('✅ Video preview converted to PIL Image successfully!')
                        else:
                            print('⚠️ Failed to generate video preview')

                    except Exception as e:
                        print(f'❌ Video conversion failed: {e}')
                        import traceback
                        traceback.print_exc()

                return result

            # Заменить метод convert
            print('🔄 Replacing convert method...')
            Python.convert = patched_convert
            print('✅ Video converter backend patched successfully!')

        except Exception as e:
            print(f'❌ Failed to patch converter backend: {e}')
            import traceback
            traceback.print_exc()
