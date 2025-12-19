"""
Management command to analyze all documents with pending or processing status.
"""
from django.core.management.base import BaseCommand
from django.utils import timezone

from mayan.apps.dam.models import DocumentAIAnalysis
from mayan.apps.documents.models import Document
from mayan.apps.dam.tasks import analyze_document_with_ai


class Command(BaseCommand):
    help = 'Analyze all documents with pending or processing AI analysis status.'

    def add_arguments(self, parser):
        parser.add_argument(
            '--status',
            action='store',
            dest='status',
            default='processing,pending',
            help='Comma-separated list of statuses to process (default: processing,pending)',
            type=str
        )
        parser.add_argument(
            '--force',
            action='store_true',
            dest='force',
            default=False,
            help='Force re-analysis even for completed documents',
        )
        parser.add_argument(
            '--limit',
            action='store',
            dest='limit',
            default=None,
            help='Limit number of documents to process',
            type=int
        )

    def handle(self, *args, **options):
        status_filter = options['status'].split(',')
        force = options['force']
        limit = options.get('limit')

        self.stdout.write('Starting analysis of pending/processing documents...\n')

        # Get all AI analysis records with specified statuses
        queryset = DocumentAIAnalysis.objects.filter(
            analysis_status__in=status_filter
        ).select_related('document')

        if limit:
            queryset = queryset[:limit]

        count = queryset.count()
        self.stdout.write(
            self.style.SUCCESS(
                f'Found {count} documents with status: {", ".join(status_filter)}'
            )
        )

        if count == 0:
            self.stdout.write(
                self.style.WARNING('No documents found to analyze.')
            )
            return

        # Process each document
        success_count = 0
        error_count = 0

        for ai_analysis in queryset:
            document = ai_analysis.document
            
            # Reset status to pending if it's stuck in processing
            if ai_analysis.analysis_status == 'processing':
                self.stdout.write(
                    f'Resetting status from "processing" to "pending" for document {document.id} ({document.label})'
                )
                ai_analysis.analysis_status = 'pending'
                ai_analysis.error_message = None
                ai_analysis.current_step = 'Queued for re-analysis'
                ai_analysis.save()

            try:
                # Schedule analysis task
                analyze_document_with_ai.delay(document_id=document.id)
                success_count += 1
                self.stdout.write(
                    self.style.SUCCESS(
                        f'✓ Scheduled analysis for document {document.id} ({document.label})'
                    )
                )
            except Exception as e:
                error_count += 1
                self.stdout.write(
                    self.style.ERROR(
                        f'✗ Failed to schedule analysis for document {document.id} ({document.label}): {e}'
                    )
                )

        self.stdout.write('\n')
        self.stdout.write(
            self.style.SUCCESS(
                f'Analysis scheduling completed: {success_count} scheduled, {error_count} errors'
            )
        )
