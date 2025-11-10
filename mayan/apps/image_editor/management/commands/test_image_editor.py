from django.core.management.base import BaseCommand
from mayan.apps.documents.models import DocumentFile


class Command(BaseCommand):
    help = 'Test image editor file access'

    def add_arguments(self, parser):
        parser.add_argument('file_id', type=int, help='DocumentFile ID to test')

    def handle(self, *args, **options):
        file_id = options['file_id']
        self.stdout.write(f'Testing access to DocumentFile ID={file_id}')

        try:
            # Проверяем через objects.all()
            file_obj = DocumentFile.objects.get(pk=file_id)
            self.stdout.write(
                self.style.SUCCESS(f'File found via objects.all(): {file_obj}')
            )
            self.stdout.write(f'  Filename: {file_obj.filename}')
            self.stdout.write(f'  MIME: {file_obj.mimetype}')
            self.stdout.write(f'  Size: {file_obj.size}')

            # Проверяем через valid manager
            try:
                valid_file = DocumentFile.valid.get(pk=file_id)
                self.stdout.write(
                    self.style.SUCCESS(f'File also accessible via .valid: {valid_file}')
                )
            except DocumentFile.DoesNotExist:
                self.stdout.write(
                    self.style.WARNING(f'File NOT accessible via .valid manager')
                )

            # Проверяем URL генерацию
            try:
                api_url = file_obj.get_api_image_url()
                self.stdout.write(f'  API URL: {api_url}')
            except Exception as e:
                self.stdout.write(
                    self.style.ERROR(f'  API URL error: {e}')
                )

        except DocumentFile.DoesNotExist:
            self.stdout.write(
                self.style.ERROR(f'File ID={file_id} does not exist')
            )
        except Exception as e:
            self.stdout.write(
                self.style.ERROR(f'Unexpected error: {e}')
            )
            import traceback
            traceback.print_exc()
