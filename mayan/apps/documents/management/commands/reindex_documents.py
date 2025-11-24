"""
Management command to reindex all documents.
"""
from django.core.management.base import BaseCommand

from mayan.apps.documents.indexing_coordinator import DocumentIndexCoordinator
from mayan.apps.documents.models import Document


class Command(BaseCommand):
    help = 'Reindex all valid documents in the system.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--batch-size',
            action='store',
            dest='batch_size',
            default=100,
            help='Number of documents to process in each batch.',
            type=int
        )
        parser.add_argument(
            '--document-ids',
            action='store',
            dest='document_ids',
            default=None,
            help='Comma-separated list of document IDs to reindex. If not provided, all valid documents will be reindexed.',
            type=str
        )

    def handle(self, *args, **options):
        batch_size = options['batch_size']
        document_ids_str = options.get('document_ids')

        self.stdout.write('Starting document reindexing...\n')

        # Get document IDs
        if document_ids_str:
            # Parse comma-separated IDs
            try:
                document_ids = [int(id.strip()) for id in document_ids_str.split(',')]
                self.stdout.write(
                    self.style.SUCCESS(
                        'Found {} document IDs to reindex.'.format(len(document_ids))
                    )
                )
            except ValueError:
                self.stderr.write(
                    self.style.ERROR(
                        'Invalid document IDs format. Use comma-separated integers.'
                    )
                )
                return
        else:
            # Get all valid documents
            document_ids = list(Document.valid.values_list('pk', flat=True))
            self.stdout.write(
                self.style.SUCCESS(
                    'Found {} valid documents to reindex.'.format(len(document_ids))
                )
            )

        if not document_ids:
            self.stdout.write(
                self.style.WARNING('No documents found to reindex.')
            )
            return

        # Process in batches
        total_batches = (len(document_ids) + batch_size - 1) // batch_size
        total_success = 0
        total_errors = 0

        for i in range(0, len(document_ids), batch_size):
            batch_ids = document_ids[i:i+batch_size]
            batch_num = (i // batch_size) + 1

            self.stdout.write(
                'Processing batch {}/{} ({} documents)...'.format(
                    batch_num, total_batches, len(batch_ids)
                )
            )

            try:
                result = DocumentIndexCoordinator.index_document_batch(
                    document_ids=batch_ids,
                    fail_fast=False
                )

                success_count = result.get('success_count', 0)
                error_count = result.get('error_count', 0)
                total_success += success_count
                total_errors += error_count

                if success_count > 0:
                    self.stdout.write(
                        self.style.SUCCESS(
                            '  ✓ Successfully scheduled: {}'.format(success_count)
                        )
                    )

                if error_count > 0:
                    self.stderr.write(
                        self.style.ERROR(
                            '  ✗ Errors: {}'.format(error_count)
                        )
                    )
                    errors = result.get('errors', [])
                    for error in errors[:3]:  # Show first 3 errors
                        self.stderr.write(
                            self.style.ERROR('    - {}'.format(error))
                        )
                    if len(errors) > 3:
                        self.stderr.write(
                            self.style.ERROR(
                                '    ... and {} more errors'.format(len(errors) - 3)
                            )
                        )

            except Exception as e:
                self.stderr.write(
                    self.style.ERROR(
                        '  ✗ Error processing batch: {}'.format(e)
                    )
                )
                total_errors += len(batch_ids)

        # Summary
        self.stdout.write('\n' + '='*60)
        self.stdout.write(
            self.style.SUCCESS(
                'Reindexing completed!'
            )
        )
        self.stdout.write(
            '  Total documents: {}'.format(len(document_ids))
        )
        self.stdout.write(
            self.style.SUCCESS(
                '  Successfully scheduled: {}'.format(total_success)
            )
        )
        if total_errors > 0:
            self.stdout.write(
                self.style.ERROR(
                    '  Errors: {}'.format(total_errors)
                )
            )
        self.stdout.write('='*60)
        self.stdout.write(
            '\nNote: Indexing tasks are scheduled asynchronously. '
            'Check Celery logs to verify execution.\n'
        )

