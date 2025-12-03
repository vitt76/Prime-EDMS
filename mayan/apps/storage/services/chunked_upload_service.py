"""
Chunked Upload Service for S3 Multipart Upload.
Phase B3.2 - Handles S3 multipart upload operations.
"""
import logging
import uuid
from datetime import datetime
from io import BytesIO

from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

logger = logging.getLogger(__name__)


class S3ServiceUnavailableError(Exception):
    """Raised when S3 service is unavailable."""
    pass


class S3UploadError(Exception):
    """Raised when S3 upload operation fails."""
    pass


class ChunkedUploadService:
    """
    Service for handling S3 Multipart Uploads.
    
    Supports Beget S3 with proper configuration for path-style addressing
    and signature version 's3' for compatibility.
    """

    def __init__(self):
        """Initialize the service with S3 configuration."""
        self._client = None
        self._config = None

    @property
    def config(self):
        """Lazy-load S3 configuration."""
        if self._config is None:
            self._config = self._load_s3_config()
        return self._config

    @property
    def client(self):
        """Lazy-load boto3 S3 client."""
        if self._client is None:
            self._client = self._create_s3_client()
        return self._client

    def _load_s3_config(self):
        """Load S3 configuration from settings."""
        try:
            from mayan.apps.storage.settings import (
                setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
                setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
                setting_s3_use_ssl, setting_s3_verify, setting_s3_location
            )

            if not setting_s3_enabled.value:
                raise ImproperlyConfigured(
                    'S3 storage is not enabled. Set STORAGE_S3_ENABLED=true'
                )

            return {
                'endpoint_url': setting_s3_endpoint_url.value,
                'access_key': setting_s3_access_key.value,
                'secret_key': setting_s3_secret_key.value,
                'bucket_name': setting_s3_bucket_name.value,
                'region_name': setting_s3_region_name.value or 'ru-1',
                'use_ssl': setting_s3_use_ssl.value,
                'verify': setting_s3_verify.value,
                'location': setting_s3_location.value or '',
            }
        except Exception as e:
            logger.error(f'Failed to load S3 config: {e}')
            raise S3ServiceUnavailableError(f'S3 configuration error: {e}')

    def _create_s3_client(self):
        """Create boto3 S3 client with Beget-compatible configuration."""
        try:
            import boto3
            from botocore.config import Config
            from botocore.exceptions import ClientError, EndpointConnectionError

            # Use s3v4 signature for better compatibility with Beget S3
            client_config = Config(
                s3={'addressing_style': 'path'},
                signature_version='s3v4',
                request_checksum_calculation='when_required',
                connect_timeout=30,
                read_timeout=60,
                retries={'max_attempts': 3, 'mode': 'adaptive'}
            )

            return boto3.client(
                's3',
                aws_access_key_id=self.config['access_key'],
                aws_secret_access_key=self.config['secret_key'],
                endpoint_url=self.config['endpoint_url'],
                region_name=self.config['region_name'],
                use_ssl=self.config['use_ssl'],
                verify=self.config['verify'],
                config=client_config
            )
        except Exception as e:
            logger.error(f'Failed to create S3 client: {e}')
            raise S3ServiceUnavailableError(f'S3 client creation failed: {e}')

    def generate_s3_key(self, filename, prefix='uploads'):
        """
        Generate a unique S3 key for the uploaded file.
        
        Format: {location}/{prefix}/{year}/{month}/{day}/{uuid}_{filename}
        """
        now = datetime.utcnow()
        unique_id = uuid.uuid4().hex[:12]
        
        # Sanitize filename
        safe_filename = ''.join(c for c in filename if c.isalnum() or c in '._-')
        if not safe_filename:
            safe_filename = 'unnamed_file'
        
        parts = [
            self.config.get('location', '').strip('/'),
            prefix,
            str(now.year),
            f'{now.month:02d}',
            f'{now.day:02d}',
            f'{unique_id}_{safe_filename}'
        ]
        
        return '/'.join(p for p in parts if p)

    def initiate_multipart_upload(self, filename, content_type='application/octet-stream'):
        """
        Initiate a multipart upload in S3.
        
        Returns:
            dict: {s3_key: str, upload_id: str}
        
        Raises:
            S3ServiceUnavailableError: If S3 is unavailable
            S3UploadError: If the initiate operation fails
        """
        s3_key = self.generate_s3_key(filename)
        
        try:
            response = self.client.create_multipart_upload(
                Bucket=self.config['bucket_name'],
                Key=s3_key,
                ContentType=content_type
            )
            
            upload_id = response['UploadId']
            logger.info(f'Initiated multipart upload: key={s3_key}, upload_id={upload_id}')
            
            return {
                's3_key': s3_key,
                'upload_id': upload_id
            }
        except self.client.exceptions.NoSuchBucket:
            raise S3UploadError(f'S3 bucket does not exist: {self.config["bucket_name"]}')
        except Exception as e:
            logger.error(f'Failed to initiate multipart upload: {e}')
            raise S3ServiceUnavailableError(f'S3 service error: {e}')

    def upload_part(self, s3_key, upload_id, part_number, data):
        """
        Upload a single part of a multipart upload.
        
        Args:
            s3_key: The S3 object key
            upload_id: The multipart upload ID
            part_number: Part number (1-10000)
            data: Bytes or file-like object to upload
        
        Returns:
            dict: {etag: str, size: int}
        
        Raises:
            S3UploadError: If the upload fails
        """
        if isinstance(data, bytes):
            body = BytesIO(data)
            size = len(data)
        else:
            # Assume file-like object
            data.seek(0, 2)  # Seek to end
            size = data.tell()
            data.seek(0)  # Seek back to start
            body = data
        
        try:
            response = self.client.upload_part(
                Bucket=self.config['bucket_name'],
                Key=s3_key,
                UploadId=upload_id,
                PartNumber=part_number,
                Body=body
            )
            
            etag = response['ETag']
            logger.debug(f'Uploaded part {part_number}: key={s3_key}, etag={etag}')
            
            return {
                'etag': etag,
                'size': size
            }
        except Exception as e:
            logger.error(f'Failed to upload part {part_number}: {e}')
            raise S3UploadError(f'Part upload failed: {e}')

    def complete_multipart_upload(self, s3_key, upload_id, parts):
        """
        Complete a multipart upload.
        
        Args:
            s3_key: The S3 object key
            upload_id: The multipart upload ID
            parts: List of dicts with {PartNumber, ETag}
        
        Returns:
            dict: S3 response with Location, ETag, etc.
        
        Raises:
            S3UploadError: If completion fails
        """
        try:
            response = self.client.complete_multipart_upload(
                Bucket=self.config['bucket_name'],
                Key=s3_key,
                UploadId=upload_id,
                MultipartUpload={'Parts': parts}
            )
            
            logger.info(f'Completed multipart upload: key={s3_key}, etag={response.get("ETag")}')
            return response
        except Exception as e:
            logger.error(f'Failed to complete multipart upload: {e}')
            raise S3UploadError(f'Complete operation failed: {e}')

    def abort_multipart_upload(self, s3_key, upload_id):
        """
        Abort a multipart upload and cleanup.
        
        Args:
            s3_key: The S3 object key
            upload_id: The multipart upload ID
        """
        try:
            self.client.abort_multipart_upload(
                Bucket=self.config['bucket_name'],
                Key=s3_key,
                UploadId=upload_id
            )
            logger.info(f'Aborted multipart upload: key={s3_key}, upload_id={upload_id}')
        except Exception as e:
            logger.warning(f'Failed to abort multipart upload (may already be complete): {e}')

    def get_object_url(self, s3_key, expires_in=3600):
        """
        Generate a presigned URL for downloading the object.
        
        Args:
            s3_key: The S3 object key
            expires_in: URL expiration time in seconds (default: 1 hour)
        
        Returns:
            str: Presigned URL
        """
        try:
            url = self.client.generate_presigned_url(
                'get_object',
                Params={
                    'Bucket': self.config['bucket_name'],
                    'Key': s3_key
                },
                ExpiresIn=expires_in
            )
            return url
        except Exception as e:
            logger.error(f'Failed to generate presigned URL: {e}')
            raise S3UploadError(f'URL generation failed: {e}')

    def check_connection(self):
        """
        Check S3 connectivity.
        
        Returns:
            tuple: (success: bool, message: str)
        """
        try:
            self.client.head_bucket(Bucket=self.config['bucket_name'])
            return True, 'S3 connection successful'
        except Exception as e:
            return False, f'S3 connection failed: {e}'

    def delete_object(self, s3_key):
        """
        Delete an object from S3.
        
        Args:
            s3_key: The S3 object key to delete
        """
        try:
            self.client.delete_object(
                Bucket=self.config['bucket_name'],
                Key=s3_key
            )
            logger.info(f'Deleted S3 object: {s3_key}')
        except Exception as e:
            logger.error(f'Failed to delete S3 object: {e}')
            raise S3UploadError(f'Delete operation failed: {e}')

