from django.utils.translation import ugettext_lazy as _

from mayan.apps.smart_settings.classes import SettingNamespace

from .literals import (
    DEFAULT_DOWNLOAD_FILE_EXPIRATION_INTERVAL,
    DEFAULT_SHARED_UPLOADED_FILE_EXPIRATION_INTERVAL,
    DEFAULT_STORAGE_DOWNLOAD_FILE_STORAGE,
    DEFAULT_STORAGE_DOWNLOAD_FILE_STORAGE_ARGUMENTS,
    DEFAULT_STORAGE_SHARED_STORAGE, DEFAULT_STORAGE_SHARED_STORAGE_ARGUMENTS,
    DEFAULT_STORAGE_TEMPORARY_DIRECTORY
)

namespace = SettingNamespace(label=_('Storage'), name='storage')

setting_download_file_expiration_interval = namespace.add_setting(
    default=DEFAULT_DOWNLOAD_FILE_EXPIRATION_INTERVAL,
    global_name='DOWNLOAD_FILE_EXPIRATION_INTERVAL', help_text=_(
        'Time in seconds, after which download files will be deleted.'
    )
)
setting_download_file_storage = namespace.add_setting(
    default=DEFAULT_STORAGE_DOWNLOAD_FILE_STORAGE,
    global_name='STORAGE_DOWNLOAD_FILE_STORAGE', help_text=_(
        'A storage backend that all workers can use to generate and hold '
        'files for download.'
    )
)
setting_download_file_storage_arguments = namespace.add_setting(
    default=DEFAULT_STORAGE_DOWNLOAD_FILE_STORAGE_ARGUMENTS,
    global_name='STORAGE_DOWNLOAD_FILE_STORAGE_ARGUMENTS',
)
setting_shared_storage = namespace.add_setting(
    default=DEFAULT_STORAGE_SHARED_STORAGE,
    global_name='STORAGE_SHARED_STORAGE', help_text=_(
        'A storage backend that all workers can use to share files.'
    )
)
setting_shared_storage_arguments = namespace.add_setting(
    default=DEFAULT_STORAGE_SHARED_STORAGE_ARGUMENTS,
    global_name='STORAGE_SHARED_STORAGE_ARGUMENTS'
)
setting_temporary_directory = namespace.add_setting(
    default=DEFAULT_STORAGE_TEMPORARY_DIRECTORY,
    global_name='STORAGE_TEMPORARY_DIRECTORY', help_text=_(
        'Temporary directory used site wide to store thumbnails, previews '
        'and temporary files.'
    )
)
setting_shared_uploaded_file_expiration_interval = namespace.add_setting(
    default=DEFAULT_SHARED_UPLOADED_FILE_EXPIRATION_INTERVAL,
    global_name='SHARED_UPLOADED_FILE_EXPIRATION_INTERVAL', help_text=_(
        'Time in seconds, after which temporary uploaded files will be '
        'deleted.'
    )
)

# S3 Storage settings
setting_s3_enabled = namespace.add_setting(
    default=False,
    global_name='STORAGE_S3_ENABLED', help_text=_(
        'Enable S3 compatible storage backend for document files. '
        'When enabled, new documents will be stored in S3 instead of local filesystem.'
    )
)
setting_s3_endpoint_url = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_ENDPOINT_URL', help_text=_(
        'S3 compatible storage endpoint URL. For Beget S3 use https://s3.ru1.storage.beget.cloud'
    )
)
setting_s3_access_key = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_ACCESS_KEY', help_text=_(
        'S3 access key for authentication.'
    )
)
setting_s3_secret_key = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_SECRET_KEY', help_text=_(
        'S3 secret key for authentication.'
    )
)
setting_s3_bucket_name = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_BUCKET_NAME', help_text=_(
        'S3 bucket name where documents will be stored.'
    )
)
setting_s3_region_name = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_REGION_NAME', help_text=_(
        'S3 region name. For Beget S3 use ru-1'
    )
)
setting_s3_use_ssl = namespace.add_setting(
    default=True,
    global_name='STORAGE_S3_USE_SSL', help_text=_(
        'Use SSL/TLS for S3 connections.'
    )
)
setting_s3_verify = namespace.add_setting(
    default=True,
    global_name='STORAGE_S3_VERIFY', help_text=_(
        'Verify SSL certificates for S3 connections. Set to False for self-signed certificates.'
    )
)

setting_s3_location = namespace.add_setting(
    default='',
    global_name='STORAGE_S3_LOCATION', help_text=_(
        'Optional prefix (folder) within the S3 bucket where all documents will be stored.'
    )
)

setting_s3_distribution_location = namespace.add_setting(
    default='PRIME/publications',
    global_name='STORAGE_S3_DISTRIBUTION_LOCATION', help_text=_(
        'Optional prefix (folder) within the S3 bucket where generated distribution renditions will be stored.'
    )
)