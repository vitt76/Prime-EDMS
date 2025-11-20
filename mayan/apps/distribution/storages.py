from botocore.config import Config
from django.utils.translation import ugettext_lazy as _

from mayan.apps.storage.classes import DefinedStorage
from mayan.apps.storage.settings import (
    setting_s3_access_key, setting_s3_bucket_name, setting_s3_endpoint_url,
    setting_s3_enabled, setting_s3_region_name, setting_s3_secret_key,
    setting_s3_use_ssl, setting_s3_verify, setting_s3_distribution_location
)

from .literals import STORAGE_NAME_DISTRIBUTION_RENDITIONS
from .settings import setting_distribution_storage


def get_distribution_storage_backend():
    if (
        setting_distribution_storage.value == 's3'
        and setting_s3_enabled.value
    ):
        return 'mayan.apps.documents.storages.BegetS3Boto3Storage'

    # Default backend: local filesystem storage rooted at MEDIA_ROOT
    return 'django.core.files.storage.FileSystemStorage'


def get_distribution_storage_kwargs():
    if (
        setting_distribution_storage.value == 's3'
        and setting_s3_enabled.value
    ):
        secret_key_value = setting_s3_secret_key.value
        client_config = Config(
            s3={
                'addressing_style': 'path'
            },
            signature_version='s3',
            request_checksum_calculation='when_required'
        )
        location = setting_s3_distribution_location.value or ''

        kwargs = {
            'access_key': setting_s3_access_key.value,
            'secret_key': secret_key_value,
            'bucket_name': setting_s3_bucket_name.value,
            'endpoint_url': setting_s3_endpoint_url.value,
            'region_name': setting_s3_region_name.value,
            'verify': setting_s3_verify.value,
            'use_ssl': setting_s3_use_ssl.value,
            'client_config': client_config,
            'addressing_style': 'path',
            'signature_version': 's3'
        }

        if location:
            kwargs['location'] = location

        return kwargs

    return {}


storage_distribution_renditions = DefinedStorage(
    dotted_path=get_distribution_storage_backend(),
    error_message=_(
        'Unable to initialize the distribution rendition storage.'
    ),
    label=_('Distribution renditions'),
    name=STORAGE_NAME_DISTRIBUTION_RENDITIONS,
    kwargs=get_distribution_storage_kwargs()
)

