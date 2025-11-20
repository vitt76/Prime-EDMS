import os

import boto3
from botocore.config import Config
from django.utils.translation import ugettext_lazy as _
from storages.backends.s3boto3 import S3Boto3Storage
from storages.utils import ReadBytesWrapper, clean_name, is_seekable

from mayan.apps.storage.classes import DefinedStorage
from mayan.apps.storage.settings import setting_s3_location
class BegetS3Boto3Storage(S3Boto3Storage):
    """
    Custom storage backend that bypasses boto3's TransferManager to avoid
    SignatureDoesNotMatch responses from Beget S3 when using upload_fileobj.
    """

    def _save(self, name, content):
        cleaned_name = clean_name(name)
        name = self._normalize_name(cleaned_name)
        params = self._get_write_parameters(name, content)

        if is_seekable(content):
            content.seek(0, os.SEEK_SET)

        upload_content = ReadBytesWrapper(content)

        if (
            self.gzip
            and params["ContentType"] in self.gzip_content_types
            and "ContentEncoding" not in params
        ):
            upload_content = self._compress_content(upload_content)
            params["ContentEncoding"] = "gzip"

        original_close = content.close
        content.close = lambda: None
        client = boto3.client(
            's3',
            aws_access_key_id=self.access_key,
            aws_secret_access_key=self.secret_key,
            aws_session_token=self.security_token,
            endpoint_url=self.endpoint_url,
            region_name=self.region_name,
            use_ssl=self.use_ssl,
            verify=self.verify,
            config=self.client_config
        )

        try:
            client.put_object(
                Bucket=self.bucket_name, Key=name, Body=upload_content, **params
            )
        finally:
            content.close = original_close

        return cleaned_name


from .literals import (
    STORAGE_NAME_DOCUMENT_FILES, STORAGE_NAME_DOCUMENT_FILE_PAGE_IMAGE_CACHE,
    STORAGE_NAME_DOCUMENT_VERSION_PAGE_IMAGE_CACHE
)
from .settings import (
    setting_document_file_storage_backend,
    setting_document_file_storage_backend_arguments,
    setting_document_file_page_image_cache_storage_backend,
    setting_document_file_page_image_cache_storage_backend_arguments,
    setting_document_version_page_image_cache_storage_backend,
    setting_document_version_page_image_cache_storage_backend_arguments
)


def get_document_storage_backend():
    """Dynamically choose storage backend based on S3 settings."""
    try:
        from mayan.apps.storage.settings import setting_s3_enabled
        print(f"DEBUG: get_document_storage_backend - S3 enabled = {setting_s3_enabled.value}")
        print(f"DEBUG: get_document_storage_backend - S3 raw_value = {getattr(setting_s3_enabled, 'raw_value', 'N/A')}")
        if setting_s3_enabled.value:
            print("DEBUG: get_document_storage_backend - Returning S3 backend")
            return 'mayan.apps.documents.storages.BegetS3Boto3Storage'
        else:
            print("DEBUG: get_document_storage_backend - Returning default backend")
    except ImportError as e:
        print(f"DEBUG: get_document_storage_backend - ImportError: {e}")
        pass
    result = setting_document_file_storage_backend.value
    print(f"DEBUG: get_document_storage_backend - Returning default: {result}")
    return result


def get_document_storage_kwargs():
    """Dynamically choose storage kwargs based on S3 settings."""
    try:
        from mayan.apps.storage.settings import (
            setting_s3_enabled, setting_s3_access_key, setting_s3_secret_key,
            setting_s3_bucket_name, setting_s3_endpoint_url, setting_s3_region_name,
            setting_s3_use_ssl, setting_s3_verify
        )
        print(f'STORAGE_KWARGS: S3 enabled = {setting_s3_enabled.value}')
        if setting_s3_enabled.value:
            secret_key_value = setting_s3_secret_key.value
            client_config = Config(
                s3={
                    'addressing_style': 'path'
                },
                signature_version='s3',
                request_checksum_calculation='when_required'
            )

            location = setting_s3_location.value or ''

            kwargs = {
                'access_key': setting_s3_access_key.value,
                'secret_key': secret_key_value,
                'bucket_name': setting_s3_bucket_name.value,
                'endpoint_url': setting_s3_endpoint_url.value,
                'region_name': setting_s3_region_name.value,
                'verify': setting_s3_verify.value,
                'use_ssl': setting_s3_use_ssl.value,
                'client_config': client_config,
                # Параметры для совместимости с Beget S3
                'addressing_style': 'path',
                'signature_version': 's3',  # Используем s3 для Beget
            }
            if location:
                kwargs['location'] = location
            print(f'STORAGE_KWARGS: Returning S3 kwargs: {list(kwargs.keys())}')
            return kwargs
    except Exception as e:
        print(f'STORAGE_KWARGS: Exception: {e}')
        pass
    result = setting_document_file_storage_backend_arguments.value
    print(f'STORAGE_KWARGS: Returning default kwargs: {result}')
    return result

storage_document_files = DefinedStorage(
    dotted_path=get_document_storage_backend(),
    error_message=_(
        'Unable to initialize the document file storage. Check '
        'the settings {} and {} for formatting errors.'.format(
            setting_document_file_storage_backend.global_name,
            setting_document_file_storage_backend_arguments.global_name
        )
    ),
    label=_('Document files'),
    name=STORAGE_NAME_DOCUMENT_FILES,
    kwargs=get_document_storage_kwargs()
)

storage_document_file_image_cache = DefinedStorage(
    dotted_path=setting_document_file_page_image_cache_storage_backend.value,
    error_message=_(
        'Unable to initialize the document file image storage. Check '
        'the settings {} and {} for formatting errors.'.format(
            setting_document_file_page_image_cache_storage_backend.global_name,
            setting_document_file_page_image_cache_storage_backend_arguments.global_name
        )
    ),
    label=_('Document file page images'),
    name=STORAGE_NAME_DOCUMENT_FILE_PAGE_IMAGE_CACHE,
    kwargs=setting_document_file_page_image_cache_storage_backend_arguments.value
)

storage_document_version_image_cache = DefinedStorage(
    dotted_path=setting_document_version_page_image_cache_storage_backend.value,
    error_message=_(
        'Unable to initialize the document version image storage. Check '
        'the settings {} and {} for formatting errors.'.format(
            setting_document_version_page_image_cache_storage_backend.global_name,
            setting_document_version_page_image_cache_storage_backend_arguments.global_name
        )
    ),
    label=_('Document version page images'),
    name=STORAGE_NAME_DOCUMENT_VERSION_PAGE_IMAGE_CACHE,
    kwargs=setting_document_version_page_image_cache_storage_backend_arguments.value
)
