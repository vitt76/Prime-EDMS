"""
Storage-related views for Headless API.

These endpoints are intended for the SPA admin UI (`/admin/storage`) to show
real Beget S3 storage info without allowing the frontend to mutate settings.

Security / safety:
- Read-only operations only (head_bucket, list_objects_v2).
- Secrets are never returned in plain text; only masked previews.
"""

import time
from dataclasses import dataclass
from typing import Dict, List, Optional, Tuple

from rest_framework import status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from mayan.apps.storage.settings import (
    setting_s3_access_key,
    setting_s3_bucket_name,
    setting_s3_enabled,
    setting_s3_endpoint_url,
    setting_s3_location,
    setting_s3_region_name,
    setting_s3_secret_key,
    setting_s3_use_ssl,
    setting_s3_verify,
    setting_s3_distribution_location,
)


@dataclass(frozen=True)
class _S3Config:
    enabled: bool
    endpoint_url: str
    bucket_name: str
    access_key: str
    secret_key: str
    region_name: str
    use_ssl: bool
    verify: bool
    location: str
    distribution_location: str


def _mask_value(value: str, prefix: int = 4, suffix: int = 4) -> str:
    if not value:
        return ''
    if len(value) <= (prefix + suffix + 3):
        return '*' * len(value)
    return f'{value[:prefix]}...{value[-suffix:]}'


def _load_s3_config() -> _S3Config:
    return _S3Config(
        enabled=bool(setting_s3_enabled.value),
        endpoint_url=str(setting_s3_endpoint_url.value or '').strip(),
        bucket_name=str(setting_s3_bucket_name.value or '').strip(),
        access_key=str(setting_s3_access_key.value or '').strip(),
        secret_key=str(setting_s3_secret_key.value or '').strip(),
        region_name=str(setting_s3_region_name.value or 'ru-1').strip() or 'ru-1',
        use_ssl=bool(setting_s3_use_ssl.value),
        verify=bool(setting_s3_verify.value),
        location=str(setting_s3_location.value or '').strip().strip('/'),
        distribution_location=str(setting_s3_distribution_location.value or '').strip().strip('/'),
    )


def _create_s3_client(config: _S3Config):
    import boto3
    from botocore.config import Config as BotoConfig

    # Use path-style + s3v4 signature for Beget compatibility.
    client_config = BotoConfig(
        s3={'addressing_style': 'path'},
        signature_version='s3v4',
        connect_timeout=10,
        read_timeout=30,
        retries={'max_attempts': 2, 'mode': 'adaptive'},
    )

    return boto3.client(
        's3',
        aws_access_key_id=config.access_key,
        aws_secret_access_key=config.secret_key,
        endpoint_url=config.endpoint_url,
        region_name=config.region_name,
        use_ssl=config.use_ssl,
        verify=config.verify,
        config=client_config,
    )


def _check_s3_connection(config: _S3Config) -> Tuple[bool, str]:
    if not config.enabled:
        return False, 'S3 disabled'
    if not (config.endpoint_url and config.bucket_name and config.access_key and config.secret_key):
        return False, 'S3 config incomplete'

    try:
        client = _create_s3_client(config=config)
        client.head_bucket(Bucket=config.bucket_name)
        client.list_objects_v2(Bucket=config.bucket_name, MaxKeys=1)
        return True, 'OK'
    except Exception as exc:
        return False, str(exc)


def _normalize_prefix(prefix: str) -> str:
    prefix = (prefix or '').strip().strip('/')
    if not prefix:
        return ''
    return f'{prefix}/'


def _categorize_key(key: str, prefixes: Dict[str, str]) -> str:
    # prefixes: category -> normalized_prefix (with trailing slash or empty)
    for category, normalized in prefixes.items():
        if normalized and key.startswith(normalized):
            return category
    return 'other'


class HeadlessS3ConfigView(APIView):
    """
    Read-only S3 config for the SPA.

    GET /api/v4/headless/storage/s3/config/
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)

        config = _load_s3_config()
        connected, message = _check_s3_connection(config=config)

        return Response(
            {
                'config': {
                    'enabled': config.enabled,
                    'endpoint_url': config.endpoint_url,
                    'bucket_name': config.bucket_name,
                    'region_name': config.region_name,
                    'use_ssl': config.use_ssl,
                    'verify': config.verify,
                    'location': config.location,
                    'distribution_location': config.distribution_location,
                    'access_key_masked': _mask_value(config.access_key),
                    'secret_key_masked': ('********' if config.secret_key else ''),
                },
                'connection': {
                    'connected': bool(connected),
                    'message': message,
                },
                'source': 'settings',  # storage settings resolve env or DB
            }
        )


class HeadlessS3StatsView(APIView):
    """
    Return real S3 bucket stats for SPA admin UI.

    GET /api/v4/headless/storage/s3/stats/?max_objects=20000

    Notes:
    - Listing objects is O(N). To keep this endpoint safe, it has a cap.
    - Response includes `is_partial=true` if the cap is reached.
    """

    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        if not (getattr(user, 'is_staff', False) or getattr(user, 'is_superuser', False)):
            return Response({'error': 'access_denied'}, status=status.HTTP_403_FORBIDDEN)

        config = _load_s3_config()
        connected, message = _check_s3_connection(config=config)

        # If not connected, still return config info to help debugging in UI.
        if not connected:
            return Response(
                {
                    'connection': {'connected': False, 'message': message},
                    'stats': {
                        'bucket_name': config.bucket_name,
                        'total_objects': 0,
                        'total_size': 0,
                        'is_partial': False,
                        'scanned_objects': 0,
                        'elapsed_ms': 0,
                        'breakdown': {},
                        'recent_objects': [],
                    },
                }
            )

        try:
            max_objects_raw = request.query_params.get('max_objects', '20000')
            max_objects = int(max_objects_raw)
        except Exception:
            max_objects = 20000
        if max_objects <= 0:
            max_objects = 20000
        if max_objects > 200000:
            max_objects = 200000

        client = _create_s3_client(config=config)

        start = time.time()
        total_objects = 0
        total_size = 0
        scanned_objects = 0
        is_partial = False

        # Virtual "buckets" based on prefixes used by the app.
        prefixes = {
            'documents': _normalize_prefix(config.location),
            'publications': _normalize_prefix(config.distribution_location),
        }
        breakdown: Dict[str, Dict[str, int]] = {
            'documents': {'objects': 0, 'size': 0},
            'publications': {'objects': 0, 'size': 0},
            'other': {'objects': 0, 'size': 0},
        }

        # Keep last 5 objects by last_modified.
        recent: List[Dict[str, object]] = []

        continuation_token: Optional[str] = None
        while True:
            kwargs = {'Bucket': config.bucket_name, 'MaxKeys': 1000}
            if continuation_token:
                kwargs['ContinuationToken'] = continuation_token

            response = client.list_objects_v2(**kwargs)
            contents = response.get('Contents') or []

            for obj in contents:
                key = obj.get('Key') or ''
                size = int(obj.get('Size') or 0)
                last_modified = obj.get('LastModified')

                total_objects += 1
                total_size += size
                scanned_objects += 1

                category = _categorize_key(key=key, prefixes=prefixes)
                breakdown.setdefault(category, {'objects': 0, 'size': 0})
                breakdown[category]['objects'] += 1
                breakdown[category]['size'] += size

                if last_modified is not None:
                    recent.append(
                        {
                            'key': key,
                            'size': size,
                            'last_modified': getattr(last_modified, 'isoformat', lambda: str(last_modified))(),
                        }
                    )
                    # Keep only top 5 most recent.
                    recent.sort(key=lambda x: x.get('last_modified') or '', reverse=True)
                    if len(recent) > 5:
                        recent = recent[:5]

                if scanned_objects >= max_objects:
                    is_partial = True
                    break

            if is_partial:
                break

            if response.get('IsTruncated'):
                continuation_token = response.get('NextContinuationToken')
                if not continuation_token:
                    break
            else:
                break

        elapsed_ms = int((time.time() - start) * 1000)

        return Response(
            {
                'connection': {'connected': True, 'message': 'OK'},
                'stats': {
                    'bucket_name': config.bucket_name,
                    'endpoint_url': config.endpoint_url,
                    'region_name': config.region_name,
                    'total_objects': total_objects,
                    'total_size': total_size,
                    'is_partial': is_partial,
                    'scanned_objects': scanned_objects,
                    'elapsed_ms': elapsed_ms,
                    'breakdown': breakdown,
                    'recent_objects': recent,
                },
            }
        )


