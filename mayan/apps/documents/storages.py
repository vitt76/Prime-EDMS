from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.classes import DefinedStorage

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
        if setting_s3_enabled.value:
            return 'storages.backends.s3boto3.S3Boto3Storage'
    except ImportError:
        pass
    return setting_document_file_storage_backend.value


def get_document_storage_kwargs():
    """Dynamically choose storage kwargs based on S3 settings."""
    try:
        from mayan.apps.storage.settings import (
            setting_s3_enabled, setting_s3_access_key, setting_s3_secret_key,
            setting_s3_bucket_name, setting_s3_endpoint_url, setting_s3_region_name,
            setting_s3_verify
        )
        if setting_s3_enabled.value:
            return {
                'access_key': setting_s3_access_key.value,
                'secret_key': setting_s3_secret_key.value,
                'bucket_name': setting_s3_bucket_name.value,
                'endpoint_url': setting_s3_endpoint_url.value,
                'region_name': setting_s3_region_name.value,
                'verify': setting_s3_verify.value,
                'default_acl': 'private',
                'file_overwrite': False,
            }
    except ImportError:
        pass
    return setting_document_file_storage_backend_arguments.value

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
