from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from mayan.apps.documents.models import Document, DocumentType


class Command(BaseCommand):
    help = 'Create a test document for testing the converter extension'

    def handle(self, *args, **options):
        # Get or create document type
        document_type, created = DocumentType.objects.get_or_create(
            name='Test Documents',
            defaults={'label': 'Test Documents'}
        )

        # Create test document
        document = Document(
            document_type=document_type,
            label='Test Document for Converter'
        )
        document.save()

        # Create document file
        test_content = b'This is a test document content for testing the converter extension.'
        content_file = ContentFile(test_content, name='test_document.txt')

        from mayan.apps.documents.models import DocumentFile
        document_file = DocumentFile(
            document=document,
            file=content_file
        )
        document_file.save()

        self.stdout.write(
            self.style.SUCCESS(f'Successfully created test document with ID {document.pk} and file ID {document_file.pk}')
        )

