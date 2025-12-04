"""
Chunked Upload Models for S3 Multipart Upload support.
Phase B3.2 - Chunked Upload API Support.
"""
import uuid
import logging
from datetime import timedelta

from django.conf import settings
from django.db import models
from django.utils import timezone
from django.utils.translation import ugettext_lazy as _

from .literals import (
    CHUNKED_UPLOAD_STATUS_PENDING,
    CHUNKED_UPLOAD_STATUS_UPLOADING,
    CHUNKED_UPLOAD_STATUS_COMPLETED,
    CHUNKED_UPLOAD_STATUS_ABORTED,
    CHUNKED_UPLOAD_STATUS_FAILED
)

logger = logging.getLogger(__name__)


class ChunkedUploadManager(models.Manager):
    """Manager for ChunkedUpload with utility methods."""

    def create_upload(self, filename, total_size, content_type='application/octet-stream', user=None):
        """Create a new chunked upload session."""
        upload = self.create(
            filename=filename,
            total_size=total_size,
            content_type=content_type,
            user=user,
            status=CHUNKED_UPLOAD_STATUS_PENDING
        )
        return upload

    def get_expired(self, hours=24):
        """Get uploads older than specified hours that are not completed."""
        cutoff = timezone.now() - timedelta(hours=hours)
        return self.filter(
            datetime_created__lt=cutoff
        ).exclude(
            status__in=[CHUNKED_UPLOAD_STATUS_COMPLETED, CHUNKED_UPLOAD_STATUS_ABORTED]
        )

    def cleanup_expired(self, hours=24):
        """Abort and cleanup expired upload sessions."""
        expired = self.get_expired(hours=hours)
        count = 0
        for upload in expired:
            try:
                upload.abort()
                count += 1
            except Exception as e:
                logger.error(f'Failed to cleanup upload {upload.upload_id}: {e}')
        return count


class ChunkedUpload(models.Model):
    """
    Model to track chunked upload sessions for S3 Multipart Upload.
    
    Flow:
    1. Client calls /api/v4/uploads/init/ -> Creates ChunkedUpload, initiates S3 multipart
    2. Client calls /api/v4/uploads/append/ for each chunk -> Uploads part to S3
    3. Client calls /api/v4/uploads/complete/ -> Completes S3 multipart, creates Document
    """
    
    STATUS_CHOICES = [
        (CHUNKED_UPLOAD_STATUS_PENDING, _('Pending')),
        (CHUNKED_UPLOAD_STATUS_UPLOADING, _('Uploading')),
        (CHUNKED_UPLOAD_STATUS_COMPLETED, _('Completed')),
        (CHUNKED_UPLOAD_STATUS_ABORTED, _('Aborted')),
        (CHUNKED_UPLOAD_STATUS_FAILED, _('Failed')),
    ]

    upload_id = models.UUIDField(
        default=uuid.uuid4,
        editable=False,
        unique=True,
        db_index=True,
        verbose_name=_('Upload ID')
    )
    
    # File information
    filename = models.CharField(
        max_length=512,
        verbose_name=_('Filename')
    )
    total_size = models.BigIntegerField(
        verbose_name=_('Total Size'),
        help_text=_('Total file size in bytes')
    )
    content_type = models.CharField(
        max_length=255,
        default='application/octet-stream',
        verbose_name=_('Content Type')
    )
    
    # Upload progress
    uploaded_size = models.BigIntegerField(
        default=0,
        verbose_name=_('Uploaded Size'),
        help_text=_('Bytes uploaded so far')
    )
    chunks_received = models.PositiveIntegerField(
        default=0,
        verbose_name=_('Chunks Received')
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default=CHUNKED_UPLOAD_STATUS_PENDING,
        db_index=True,
        verbose_name=_('Status')
    )
    
    # S3 Multipart Upload tracking
    s3_upload_id = models.CharField(
        max_length=255,
        blank=True,
        null=True,
        verbose_name=_('S3 Upload ID'),
        help_text=_('S3 Multipart Upload ID')
    )
    s3_key = models.CharField(
        max_length=1024,
        blank=True,
        null=True,
        verbose_name=_('S3 Key'),
        help_text=_('S3 object key for the uploaded file')
    )
    
    # Parts tracking (JSON array of {part_number, etag, size})
    parts_info = models.JSONField(
        default=list,
        blank=True,
        verbose_name=_('Parts Info'),
        help_text=_('JSON array of uploaded parts metadata')
    )
    
    # User and timestamps
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        verbose_name=_('User')
    )
    datetime_created = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_('Created')
    )
    datetime_updated = models.DateTimeField(
        auto_now=True,
        verbose_name=_('Updated')
    )
    datetime_completed = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name=_('Completed')
    )
    
    # Result tracking
    document_id = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name=_('Document ID'),
        help_text=_('ID of created document after successful upload')
    )
    error_message = models.TextField(
        blank=True,
        null=True,
        verbose_name=_('Error Message')
    )

    objects = ChunkedUploadManager()

    class Meta:
        verbose_name = _('Chunked Upload')
        verbose_name_plural = _('Chunked Uploads')
        ordering = ['-datetime_created']
        indexes = [
            models.Index(fields=['upload_id']),
            models.Index(fields=['status', 'datetime_created']),
            models.Index(fields=['user', 'status']),
        ]

    def __str__(self):
        return f'{self.filename} ({self.upload_id}) - {self.get_status_display()}'

    @property
    def progress_percent(self):
        """Calculate upload progress percentage."""
        if self.total_size == 0:
            return 0
        return round((self.uploaded_size / self.total_size) * 100, 2)

    @property
    def is_complete(self):
        """Check if all chunks have been received."""
        return self.uploaded_size >= self.total_size

    def add_part(self, part_number, etag, size):
        """Record uploaded part info."""
        parts = self.parts_info or []
        # Remove existing part with same number (for retries)
        parts = [p for p in parts if p.get('part_number') != part_number]
        parts.append({
            'part_number': part_number,
            'etag': etag.strip('"'),  # S3 returns ETag with quotes
            'size': size
        })
        # Sort by part number
        parts.sort(key=lambda x: x['part_number'])
        self.parts_info = parts
        self.chunks_received = len(parts)
        self.uploaded_size = sum(p['size'] for p in parts)
        self.save(update_fields=['parts_info', 'chunks_received', 'uploaded_size', 'datetime_updated'])

    def get_parts_for_complete(self):
        """Get parts list formatted for S3 CompleteMultipartUpload."""
        return [
            {'PartNumber': p['part_number'], 'ETag': p['etag']}
            for p in sorted(self.parts_info, key=lambda x: x['part_number'])
        ]

    def mark_completed(self, document_id=None):
        """Mark upload as completed."""
        self.status = CHUNKED_UPLOAD_STATUS_COMPLETED
        self.datetime_completed = timezone.now()
        if document_id:
            self.document_id = document_id
        self.save()

    def mark_failed(self, error_message):
        """Mark upload as failed."""
        self.status = CHUNKED_UPLOAD_STATUS_FAILED
        self.error_message = str(error_message)[:2000]
        self.save()

    def abort(self):
        """Abort the upload and cleanup S3 resources."""
        from .services.chunked_upload_service import ChunkedUploadService
        
        if self.s3_upload_id and self.s3_key:
            try:
                service = ChunkedUploadService()
                service.abort_multipart_upload(self.s3_key, self.s3_upload_id)
            except Exception as e:
                logger.error(f'Failed to abort S3 multipart upload: {e}')
        
        self.status = CHUNKED_UPLOAD_STATUS_ABORTED
        self.save()


