#!/usr/bin/env python3
"""
Mock-to-S3 Bridge Migration Script
===================================

Downloads Unsplash placeholder images and uploads them to S3 (Beget Cloud).
Generates a mapping file for frontend consumption.

Usage:
    python scripts/migrate_mocks.py

Output:
    - Images uploaded to S3: PRIME/documents/asset_*.jpg
    - Mapping file: frontend/src/mocks/s3_map.json

Requirements:
    pip install boto3 requests
"""

import os
import sys
import json
import hashlib
import tempfile
import logging
from pathlib import Path
from typing import Dict, List, Optional
from concurrent.futures import ThreadPoolExecutor, as_completed

try:
    import boto3
    from botocore.config import Config
    from botocore.exceptions import ClientError
except ImportError:
    print("Error: boto3 not installed. Run: pip install boto3")
    sys.exit(1)

try:
    import requests
except ImportError:
    print("Error: requests not installed. Run: pip install requests")
    sys.exit(1)

# ============================================================================
# CONFIGURATION
# ============================================================================

# S3 Configuration (Beget Cloud)
S3_CONFIG = {
    'endpoint_url': os.getenv('MAYAN_STORAGE_S3_ENDPOINT_URL', 'https://s3.ru1.storage.beget.cloud'),
    'access_key': os.getenv('MAYAN_STORAGE_S3_ACCESS_KEY', '2EILOPQ3JUAW797ZF3DL'),
    'secret_key': os.getenv('MAYAN_STORAGE_S3_SECRET_KEY', 'RjLi6AD0OgofbJ2YbzMnHFCqudVwf9Tqw3kB9E7z'),
    'bucket_name': os.getenv('MAYAN_STORAGE_S3_BUCKET_NAME', 'cafdf4e9fa32-righteous-rimma'),
    'region_name': os.getenv('MAYAN_STORAGE_S3_REGION_NAME', 'ru-1'),
}

# Upload destination prefix in bucket
S3_PREFIX = 'PRIME/mock-assets'

# Output mapping file path
OUTPUT_MAP_FILE = Path(__file__).parent.parent / 'frontend' / 'src' / 'mocks' / 's3_map.json'

# Unsplash images from frontend/src/mocks/assets.ts
# High-quality landscape and portrait images
MOCK_IMAGES: List[Dict[str, str]] = [
    # Landscape images (400x300 aspect)
    {
        'id': 'landscape_01',
        'url': 'https://images.unsplash.com/photo-1682687220742-aba13b6e50ba?w=1200&h=900&fit=crop',
        'label': 'Горный пейзаж на закате',
        'type': 'image',
    },
    {
        'id': 'landscape_02',
        'url': 'https://images.unsplash.com/photo-1506905925346-21bda4d32df4?w=1200&h=900&fit=crop',
        'label': 'Альпийские горы',
        'type': 'image',
    },
    {
        'id': 'landscape_03',
        'url': 'https://images.unsplash.com/photo-1469474968028-56623f02e42e?w=1200&h=900&fit=crop',
        'label': 'Природа и лес',
        'type': 'image',
    },
    {
        'id': 'landscape_04',
        'url': 'https://images.unsplash.com/photo-1447752875215-b2761acb3c5d?w=1200&h=900&fit=crop',
        'label': 'Лесная тропа',
        'type': 'image',
    },
    {
        'id': 'landscape_05',
        'url': 'https://images.unsplash.com/photo-1433086966358-54859d0ed716?w=1200&h=900&fit=crop',
        'label': 'Водопад в горах',
        'type': 'image',
    },
    {
        'id': 'landscape_06',
        'url': 'https://images.unsplash.com/photo-1501854140801-50d01698950b?w=1200&h=900&fit=crop',
        'label': 'Зеленые холмы',
        'type': 'image',
    },
    {
        'id': 'landscape_07',
        'url': 'https://images.unsplash.com/photo-1470071459604-3b5ec3a7fe05?w=1200&h=900&fit=crop',
        'label': 'Туманные горы',
        'type': 'image',
    },
    {
        'id': 'landscape_08',
        'url': 'https://images.unsplash.com/photo-1441974231531-c6227db76b6e?w=1200&h=900&fit=crop',
        'label': 'Солнечный лес',
        'type': 'image',
    },
    {
        'id': 'landscape_09',
        'url': 'https://images.unsplash.com/photo-1518173946687-a4c036bc4f9a?w=1200&h=900&fit=crop',
        'label': 'Облака над горами',
        'type': 'image',
    },
    {
        'id': 'landscape_10',
        'url': 'https://images.unsplash.com/photo-1475924156734-496f6cac6ec1?w=1200&h=900&fit=crop',
        'label': 'Морской берег',
        'type': 'image',
    },
    # Portrait images (300x400 aspect)
    {
        'id': 'portrait_01',
        'url': 'https://images.unsplash.com/photo-1507003211169-0a1dd7228f2d?w=900&h=1200&fit=crop',
        'label': 'Бизнес портрет мужчина',
        'type': 'image',
    },
    {
        'id': 'portrait_02',
        'url': 'https://images.unsplash.com/photo-1494790108377-be9c29b29330?w=900&h=1200&fit=crop',
        'label': 'Бизнес портрет женщина',
        'type': 'image',
    },
    {
        'id': 'portrait_03',
        'url': 'https://images.unsplash.com/photo-1517841905240-472988babdf9?w=900&h=1200&fit=crop',
        'label': 'Молодая женщина',
        'type': 'image',
    },
    {
        'id': 'portrait_04',
        'url': 'https://images.unsplash.com/photo-1539571696357-5a69c17a67c6?w=900&h=1200&fit=crop',
        'label': 'Молодой мужчина',
        'type': 'image',
    },
    {
        'id': 'portrait_05',
        'url': 'https://images.unsplash.com/photo-1524504388940-b1c1722653e1?w=900&h=1200&fit=crop',
        'label': 'Модель в студии',
        'type': 'image',
    },
    # Video thumbnails
    {
        'id': 'video_01',
        'url': 'https://images.unsplash.com/photo-1536240478700-b869070f9279?w=1200&h=900&fit=crop',
        'label': 'Превью видео кинопроизводство',
        'type': 'video',
    },
    {
        'id': 'video_02',
        'url': 'https://images.unsplash.com/photo-1492691527719-9d1e07e534b4?w=1200&h=900&fit=crop',
        'label': 'Превью видео репортаж',
        'type': 'video',
    },
    {
        'id': 'video_03',
        'url': 'https://images.unsplash.com/photo-1574717024653-61fd2cf4d44d?w=1200&h=900&fit=crop',
        'label': 'Превью видео интервью',
        'type': 'video',
    },
    # Document thumbnail
    {
        'id': 'document_01',
        'url': 'https://images.unsplash.com/photo-1568667256549-094345857637?w=1200&h=900&fit=crop',
        'label': 'Превью документа',
        'type': 'document',
    },
    # Additional high-quality assets
    {
        'id': 'architecture_01',
        'url': 'https://images.unsplash.com/photo-1486325212027-8081e485255e?w=1200&h=900&fit=crop',
        'label': 'Современная архитектура',
        'type': 'image',
    },
    {
        'id': 'technology_01',
        'url': 'https://images.unsplash.com/photo-1518770660439-4636190af475?w=1200&h=900&fit=crop',
        'label': 'Технологии и электроника',
        'type': 'image',
    },
    {
        'id': 'food_01',
        'url': 'https://images.unsplash.com/photo-1504674900247-0877df9cc836?w=1200&h=900&fit=crop',
        'label': 'Гастрономия блюдо',
        'type': 'image',
    },
    {
        'id': 'business_01',
        'url': 'https://images.unsplash.com/photo-1556761175-4b46a572b786?w=1200&h=900&fit=crop',
        'label': 'Бизнес встреча команда',
        'type': 'image',
    },
    {
        'id': 'abstract_01',
        'url': 'https://images.unsplash.com/photo-1557672172-298e090bd0f1?w=1200&h=900&fit=crop',
        'label': 'Абстрактное искусство',
        'type': 'image',
    },
    {
        'id': 'city_01',
        'url': 'https://images.unsplash.com/photo-1480714378408-67cf0d13bc1b?w=1200&h=900&fit=crop',
        'label': 'Городской пейзаж небоскребы',
        'type': 'image',
    },
]

# Logging setup
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s [%(levelname)s] %(message)s',
    datefmt='%H:%M:%S'
)
logger = logging.getLogger(__name__)

# ============================================================================
# S3 CLIENT
# ============================================================================

def create_s3_client():
    """Create boto3 S3 client configured for Beget Cloud."""
    # Beget S3 requires specific signature configuration
    # Based on working config from mayan/apps/documents/storages.py
    config = Config(
        s3={
            'addressing_style': 'path'
        },
        signature_version='s3v4',  # Try s3v4 first
        retries={
            'max_attempts': 3,
            'mode': 'standard'
        }
    )
    
    client = boto3.client(
        's3',
        endpoint_url=S3_CONFIG['endpoint_url'],
        aws_access_key_id=S3_CONFIG['access_key'],
        aws_secret_access_key=S3_CONFIG['secret_key'],
        region_name=S3_CONFIG['region_name'],
        config=config
    )
    
    return client


def create_s3_client_v2():
    """Alternative S3 client with s3 (v2) signature."""
    config = Config(
        s3={
            'addressing_style': 'path'
        },
        signature_version='s3',
        request_checksum_calculation='when_required'
    )
    
    return boto3.client(
        's3',
        endpoint_url=S3_CONFIG['endpoint_url'],
        aws_access_key_id=S3_CONFIG['access_key'],
        aws_secret_access_key=S3_CONFIG['secret_key'],
        region_name=S3_CONFIG['region_name'],
        config=config
    )

# ============================================================================
# DOWNLOAD & UPLOAD FUNCTIONS
# ============================================================================

def download_image(url: str, timeout: int = 30, retries: int = 3) -> Optional[bytes]:
    """Download image from URL with retries."""
    import time
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Accept': 'image/webp,image/apng,image/*,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.9,ru;q=0.8',
        'Referer': 'https://unsplash.com/',
    }
    
    for attempt in range(retries):
        try:
            # Add delay between retries
            if attempt > 0:
                delay = 2 ** attempt  # Exponential backoff: 2, 4, 8 seconds
                logger.info(f"  Retry {attempt + 1}/{retries} after {delay}s delay...")
                time.sleep(delay)
            
            response = requests.get(url, timeout=timeout, headers=headers, stream=True)
            response.raise_for_status()
            return response.content
        except requests.RequestException as e:
            if attempt == retries - 1:
                logger.error(f"Failed to download {url}: {e}")
                return None
            logger.warning(f"  Download attempt {attempt + 1} failed: {e}")
    
    return None


def upload_to_s3(
    s3_client,
    data: bytes,
    s3_key: str,
    content_type: str = 'image/jpeg'
) -> bool:
    """Upload binary data to S3."""
    try:
        # First try with ACL (some S3-compatible services support it)
        try:
            s3_client.put_object(
                Bucket=S3_CONFIG['bucket_name'],
                Key=s3_key,
                Body=data,
                ContentType=content_type,
                ACL='public-read'
            )
        except ClientError as acl_error:
            # If ACL not supported, try without it
            if 'AccessControlListNotSupported' in str(acl_error) or 'InvalidArgument' in str(acl_error):
                logger.warning(f"ACL not supported, uploading without ACL...")
                s3_client.put_object(
                    Bucket=S3_CONFIG['bucket_name'],
                    Key=s3_key,
                    Body=data,
                    ContentType=content_type
                )
            else:
                raise
        return True
    except ClientError as e:
        logger.error(f"Failed to upload to S3 {s3_key}: {e}")
        return False


def get_s3_public_url(s3_key: str) -> str:
    """Generate public URL for S3 object."""
    # Beget S3 URL format: https://s3.ru1.storage.beget.cloud/BUCKET/KEY
    return f"{S3_CONFIG['endpoint_url']}/{S3_CONFIG['bucket_name']}/{s3_key}"


def process_mock_image(s3_client, mock: Dict[str, str]) -> Optional[Dict[str, str]]:
    """Download and upload a single mock image."""
    mock_id = mock['id']
    url = mock['url']
    label = mock['label']
    asset_type = mock['type']
    
    logger.info(f"Processing {mock_id}: {label}")
    
    # Download
    data = download_image(url)
    if not data:
        return None
    
    # Generate S3 key
    # Use hash for unique filename
    content_hash = hashlib.md5(data).hexdigest()[:8]
    extension = 'jpg'
    s3_key = f"{S3_PREFIX}/{mock_id}_{content_hash}.{extension}"
    
    # Upload
    if not upload_to_s3(s3_client, data, s3_key):
        return None
    
    # Generate public URL
    public_url = get_s3_public_url(s3_key)
    
    logger.info(f"✓ Uploaded {mock_id} → {public_url}")
    
    return {
        'id': mock_id,
        'label': label,
        'type': asset_type,
        's3_key': s3_key,
        's3_url': public_url,
        'original_url': url,
        'size_bytes': len(data),
    }


# ============================================================================
# MAIN MIGRATION
# ============================================================================

def migrate_mocks_to_s3() -> Dict[str, any]:
    """Main migration function."""
    logger.info("=" * 60)
    logger.info("Mock-to-S3 Bridge Migration")
    logger.info("=" * 60)
    logger.info(f"Bucket: {S3_CONFIG['bucket_name']}")
    logger.info(f"Endpoint: {S3_CONFIG['endpoint_url']}")
    logger.info(f"Prefix: {S3_PREFIX}")
    logger.info(f"Images to migrate: {len(MOCK_IMAGES)}")
    logger.info("=" * 60)
    
    # Try different S3 client configurations
    s3_client = None
    
    for client_creator, sig_name in [
        (create_s3_client, 's3v4'),
        (create_s3_client_v2, 's3')
    ]:
        logger.info(f"Trying signature version: {sig_name}")
        test_client = client_creator()
        
        try:
            # Test with a simple list operation
            test_client.list_objects_v2(
                Bucket=S3_CONFIG['bucket_name'],
                MaxKeys=1,
                Prefix=S3_PREFIX
            )
            s3_client = test_client
            logger.info(f"✓ S3 connection successful with {sig_name}")
            break
        except ClientError as e:
            error_code = e.response.get('Error', {}).get('Code', '')
            logger.warning(f"⚠ {sig_name} failed: {error_code} - {e}")
            
            # If signature mismatch, try next
            if 'SignatureDoesNotMatch' in str(e):
                continue
            
            # If access denied on list, still try uploads
            if error_code in ('AccessDenied', '403', 'Forbidden'):
                s3_client = test_client
                logger.warning(f"⚠ List denied but will attempt uploads with {sig_name}")
                break
    
    if not s3_client:
        logger.error("✗ Could not establish S3 connection with any signature version")
        return {'success': False, 'error': 'S3 connection failed with all signature versions'}
    
    # Process all images
    results = []
    failed = []
    
    import time
    
    # Process sequentially with delays to avoid rate limiting
    for i, mock in enumerate(MOCK_IMAGES):
        # Add delay between downloads (except first)
        if i > 0:
            time.sleep(1.5)  # 1.5 second delay between images
        
        try:
            result = process_mock_image(s3_client, mock)
            if result:
                results.append(result)
            else:
                failed.append(mock['id'])
        except Exception as e:
            logger.error(f"Error processing {mock['id']}: {e}")
            failed.append(mock['id'])
    
    logger.info("=" * 60)
    logger.info(f"Migration complete: {len(results)}/{len(MOCK_IMAGES)} successful")
    if failed:
        logger.warning(f"Failed: {', '.join(failed)}")
    
    # Generate mapping
    mapping = {
        'generated_at': __import__('datetime').datetime.now().isoformat(),
        'bucket': S3_CONFIG['bucket_name'],
        'endpoint': S3_CONFIG['endpoint_url'],
        'prefix': S3_PREFIX,
        'total_count': len(results),
        'total_size_bytes': sum(r['size_bytes'] for r in results),
        'assets': {r['id']: r for r in results},
        # Quick lookup by ID → URL
        'url_map': {r['id']: r['s3_url'] for r in results},
    }
    
    # Save mapping file
    OUTPUT_MAP_FILE.parent.mkdir(parents=True, exist_ok=True)
    with open(OUTPUT_MAP_FILE, 'w', encoding='utf-8') as f:
        json.dump(mapping, f, indent=2, ensure_ascii=False)
    
    logger.info(f"✓ Mapping saved to: {OUTPUT_MAP_FILE}")
    
    return {'success': True, 'mapping': mapping, 'failed': failed}


# ============================================================================
# VERIFICATION
# ============================================================================

def verify_s3_uploads():
    """Verify all uploads are accessible."""
    if not OUTPUT_MAP_FILE.exists():
        logger.error(f"Mapping file not found: {OUTPUT_MAP_FILE}")
        return False
    
    with open(OUTPUT_MAP_FILE, 'r', encoding='utf-8') as f:
        mapping = json.load(f)
    
    logger.info("Verifying S3 uploads...")
    
    all_ok = True
    for asset_id, url in mapping['url_map'].items():
        try:
            response = requests.head(url, timeout=10)
            if response.status_code == 200:
                logger.info(f"✓ {asset_id}: OK")
            else:
                logger.warning(f"✗ {asset_id}: HTTP {response.status_code}")
                all_ok = False
        except requests.RequestException as e:
            logger.error(f"✗ {asset_id}: {e}")
            all_ok = False
    
    return all_ok


# ============================================================================
# CLI
# ============================================================================

def main():
    """CLI entry point."""
    import argparse
    
    parser = argparse.ArgumentParser(description='Mock-to-S3 Bridge Migration')
    parser.add_argument(
        '--verify-only',
        action='store_true',
        help='Only verify existing uploads without migrating'
    )
    parser.add_argument(
        '--dry-run',
        action='store_true',
        help='Show what would be uploaded without actually uploading'
    )
    
    args = parser.parse_args()
    
    if args.verify_only:
        success = verify_s3_uploads()
        sys.exit(0 if success else 1)
    
    if args.dry_run:
        logger.info("DRY RUN - No actual uploads")
        for mock in MOCK_IMAGES:
            s3_key = f"{S3_PREFIX}/{mock['id']}.jpg"
            logger.info(f"Would upload: {mock['label']} → {s3_key}")
        logger.info(f"Total: {len(MOCK_IMAGES)} images")
        sys.exit(0)
    
    result = migrate_mocks_to_s3()
    
    if result['success']:
        logger.info("\n✓ Migration completed successfully!")
        logger.info(f"  Total assets: {result['mapping']['total_count']}")
        logger.info(f"  Total size: {result['mapping']['total_size_bytes'] / 1024 / 1024:.2f} MB")
        sys.exit(0)
    else:
        logger.error(f"\n✗ Migration failed: {result.get('error', 'Unknown error')}")
        sys.exit(1)


if __name__ == '__main__':
    main()

