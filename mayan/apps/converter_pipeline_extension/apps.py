from mayan.apps.common.apps import MayanAppConfig
from django.utils.translation import ugettext_lazy as _


class ConverterPipelineExtensionApp(MayanAppConfig):
    """
    Converter Pipeline Extension - расширенная система конвертеров для Mayan EDMS.
    """
    app_namespace = 'converter_pipeline_extension'
    app_url = 'converter-pipeline'
    has_rest_api = False
    has_static_media = True
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

        # Регистрация меню
        try:
            self._register_menu()
            self._patch_converter_backend()
        except Exception as e:
            print(f'❌ Failed to register extension: {e}')

        # Add middleware для JavaScript внедрения
        try:
            self._add_middleware()
        except Exception as e:
            print(f'❌ Failed to add middleware: {e}')

        # Для Vue.js SPA используем context processor
        try:
            self._add_context_processor()
        except Exception as e:
            print(f'❌ Failed to add context processor: {e}')

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

    def _register_menu(self):
        """Регистрация пункта меню"""
        try:
            from mayan.apps.common.menus import menu_object
            from mayan.apps.documents.models import DocumentFile

            from .links import link_document_file_convert

            menu_object.bind_links(
                links=(link_document_file_convert,),
                sources=(DocumentFile,)
            )

            print('✅ Menu registered successfully!')

        except Exception as e:
            print(f'❌ Failed to register menu: {e}')
            import traceback
            traceback.print_exc()

    def _add_middleware(self):
        """Add middleware for JavaScript injection"""
        try:
            from django.conf import settings

            middleware_path = 'mayan.apps.converter_pipeline_extension.middleware.ConverterJavaScriptMiddleware'

            if middleware_path not in settings.MIDDLEWARE:
                # Add our middleware to the list
                settings.MIDDLEWARE = list(settings.MIDDLEWARE) + [middleware_path]
                print('✅ Converter JavaScript middleware added')

        except Exception as e:
            print(f'❌ Failed to add middleware: {e}')
            import traceback
            traceback.print_exc()

    def _add_context_processor(self):
        """Add context processor for JavaScript injection"""
        try:
            from django.conf import settings

            processor_path = 'mayan.apps.converter_pipeline_extension.context_processors.converter_javascript'

            if processor_path not in settings.TEMPLATES[0]['OPTIONS'].get('context_processors', []):
                settings.TEMPLATES[0]['OPTIONS']['context_processors'].append(processor_path)
                print('✅ Converter JavaScript context processor added')

        except Exception as e:
            print(f'❌ Failed to add context processor: {e}')
            import traceback
            traceback.print_exc()

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
