"""
Serializers for Chunked Upload API.
Phase B3.2 - Chunked Upload API Support.
"""
from rest_framework import serializers

from .literals import (
    CHUNKED_UPLOAD_MIN_CHUNK_SIZE,
    CHUNKED_UPLOAD_MAX_CHUNK_SIZE,
    CHUNKED_UPLOAD_DEFAULT_CHUNK_SIZE,
    CHUNKED_UPLOAD_MAX_PARTS
)


class ChunkedUploadInitSerializer(serializers.Serializer):
    """Serializer for initiating a chunked upload."""
    
    filename = serializers.CharField(
        max_length=512,
        help_text='Name of the file being uploaded'
    )
    total_size = serializers.IntegerField(
        min_value=1,
        help_text='Total size of the file in bytes'
    )
    content_type = serializers.CharField(
        max_length=255,
        default='application/octet-stream',
        required=False,
        help_text='MIME type of the file'
    )
    document_type_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Document type ID for the created document'
    )
    
    def validate_total_size(self, value):
        """Validate file size is within acceptable limits."""
        max_size = 50 * 1024 * 1024 * 1024  # 50GB
        if value > max_size:
            raise serializers.ValidationError(
                f'File size exceeds maximum allowed ({max_size} bytes)'
            )
        return value


class ChunkedUploadInitResponseSerializer(serializers.Serializer):
    """Response serializer for upload initialization."""
    
    upload_id = serializers.UUIDField(help_text='Unique upload session ID')
    s3_key = serializers.CharField(help_text='S3 object key')
    chunk_size = serializers.IntegerField(help_text='Recommended chunk size in bytes')
    max_chunks = serializers.IntegerField(help_text='Maximum number of chunks')


class ChunkedUploadAppendSerializer(serializers.Serializer):
    """Serializer for appending a chunk to upload."""
    
    upload_id = serializers.UUIDField(
        help_text='Upload session ID from init response'
    )
    part_number = serializers.IntegerField(
        min_value=1,
        max_value=CHUNKED_UPLOAD_MAX_PARTS,
        help_text='Part number (1-10000)'
    )
    chunk = serializers.FileField(
        help_text='Chunk data to upload'
    )
    
    def validate_chunk(self, value):
        """Validate chunk size."""
        if value.size < CHUNKED_UPLOAD_MIN_CHUNK_SIZE:
            # Allow smaller chunks for the last part
            pass
        if value.size > CHUNKED_UPLOAD_MAX_CHUNK_SIZE:
            raise serializers.ValidationError(
                f'Chunk size exceeds maximum ({CHUNKED_UPLOAD_MAX_CHUNK_SIZE} bytes)'
            )
        return value


class ChunkedUploadAppendResponseSerializer(serializers.Serializer):
    """Response serializer for chunk append."""
    
    upload_id = serializers.UUIDField()
    part_number = serializers.IntegerField()
    etag = serializers.CharField(help_text='S3 ETag for the uploaded part')
    size = serializers.IntegerField(help_text='Size of uploaded chunk')
    uploaded_size = serializers.IntegerField(help_text='Total bytes uploaded so far')
    progress_percent = serializers.FloatField(help_text='Upload progress percentage')


class ChunkedUploadCompleteSerializer(serializers.Serializer):
    """Serializer for completing a chunked upload."""
    
    upload_id = serializers.UUIDField(
        help_text='Upload session ID'
    )
    label = serializers.CharField(
        max_length=255,
        required=False,
        help_text='Document label (defaults to filename)'
    )
    description = serializers.CharField(
        required=False,
        allow_blank=True,
        help_text='Document description'
    )
    document_type_id = serializers.IntegerField(
        required=False,
        allow_null=True,
        help_text='Document type ID'
    )


class ChunkedUploadCompleteResponseSerializer(serializers.Serializer):
    """Response serializer for upload completion."""
    
    upload_id = serializers.UUIDField()
    document_id = serializers.IntegerField(help_text='Created document ID')
    document_file_id = serializers.IntegerField(help_text='Created document file ID')
    s3_key = serializers.CharField()
    status = serializers.CharField()


class ChunkedUploadStatusSerializer(serializers.Serializer):
    """Serializer for upload status response."""
    
    upload_id = serializers.UUIDField()
    filename = serializers.CharField()
    total_size = serializers.IntegerField()
    uploaded_size = serializers.IntegerField()
    chunks_received = serializers.IntegerField()
    progress_percent = serializers.FloatField()
    status = serializers.CharField()
    s3_key = serializers.CharField(allow_null=True)
    document_id = serializers.IntegerField(allow_null=True)
    error_message = serializers.CharField(allow_null=True)
    datetime_created = serializers.DateTimeField()
    datetime_updated = serializers.DateTimeField()


class ChunkedUploadAbortSerializer(serializers.Serializer):
    """Serializer for aborting an upload."""
    
    upload_id = serializers.UUIDField(
        help_text='Upload session ID to abort'
    )


class S3ErrorResponseSerializer(serializers.Serializer):
    """Standardized error response for S3 failures."""
    
    error = serializers.CharField(help_text='Error type')
    error_code = serializers.CharField(help_text='Machine-readable error code')
    detail = serializers.CharField(help_text='Human-readable error message')
    retry_after = serializers.IntegerField(
        required=False,
        help_text='Seconds to wait before retrying'
    )









