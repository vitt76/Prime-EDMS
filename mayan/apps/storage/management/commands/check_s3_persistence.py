"""
Management command to verify S3 persistence and connectivity.
Phase B3.1 - S3 Persistence Hardening.
"""
import logging
import time
from datetime import datetime

from django.core.management.base import BaseCommand, CommandError

logger = logging.getLogger(__name__)


class Command(BaseCommand):
    help = 'Verify S3 storage persistence by uploading, reading, and deleting a test file'

    def add_arguments(self, parser):
        parser.add_argument(
            '--verbose',
            action='store_true',
            help='Enable verbose output with timing information'
        )
        parser.add_argument(
            '--keep-file',
            action='store_true',
            help='Do not delete the test file after verification'
        )
        parser.add_argument(
            '--prefix',
            type=str,
            default='_mayan_tests',
            help='S3 key prefix for test files (default: _mayan_tests)'
        )

    def handle(self, *args, **options):
        verbose = options['verbose']
        keep_file = options['keep_file']
        prefix = options['prefix']

        self.stdout.write('=' * 60)
        self.stdout.write('🔍 S3 Persistence Check')
        self.stdout.write('=' * 60)

        # Step 1: Load and validate S3 configuration
        self.stdout.write('\n📋 Step 1: Loading S3 configuration...')
        try:
            s3_config = self._load_s3_config()
            if verbose:
                self.stdout.write(f'   Endpoint: {s3_config["endpoint_url"]}')
                self.stdout.write(f'   Bucket: {s3_config["bucket_name"]}')
                self.stdout.write(f'   Region: {s3_config["region_name"]}')
            self.stdout.write(self.style.SUCCESS('   ✅ S3 configuration loaded'))
        except Exception as e:
            raise CommandError(f'❌ Failed to load S3 configuration: {e}')

        # Step 2: Create boto3 client
        self.stdout.write('\n📋 Step 2: Creating S3 client...')
        try:
            s3_client = self._create_s3_client(s3_config)
            self.stdout.write(self.style.SUCCESS('   ✅ S3 client created'))
        except Exception as e:
            raise CommandError(f'❌ Failed to create S3 client: {e}')

        # Step 3: Verify bucket access
        self.stdout.write('\n📋 Step 3: Verifying bucket access...')
        try:
            start_time = time.time()
            s3_client.head_bucket(Bucket=s3_config['bucket_name'])
            elapsed = time.time() - start_time
            if verbose:
                self.stdout.write(f'   Latency: {elapsed:.3f}s')
            self.stdout.write(self.style.SUCCESS('   ✅ Bucket is accessible'))
        except Exception as e:
            raise CommandError(f'❌ Bucket access failed: {e}')

        # Step 4: Upload test file
        timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
        test_key = f'{prefix}/s3_test_{timestamp}.txt'
        test_content = f'Mayan EDMS S3 Persistence Test\nTimestamp: {timestamp}\nTest ID: {id(self)}'

        self.stdout.write(f'\n📋 Step 4: Uploading test file ({test_key})...')
        try:
            start_time = time.time()
            s3_client.put_object(
                Bucket=s3_config['bucket_name'],
                Key=test_key,
                Body=test_content.encode('utf-8'),
                ContentType='text/plain'
            )
            upload_time = time.time() - start_time
            if verbose:
                self.stdout.write(f'   Upload time: {upload_time:.3f}s')
                self.stdout.write(f'   Content size: {len(test_content)} bytes')
            self.stdout.write(self.style.SUCCESS('   ✅ Test file uploaded'))
        except Exception as e:
            raise CommandError(f'❌ Upload failed: {e}')

        # Step 5: Verify file exists (HEAD request)
        self.stdout.write('\n📋 Step 5: Verifying file exists...')
        try:
            start_time = time.time()
            head_response = s3_client.head_object(
                Bucket=s3_config['bucket_name'],
                Key=test_key
            )
            head_time = time.time() - start_time
            if verbose:
                self.stdout.write(f'   HEAD latency: {head_time:.3f}s')
                self.stdout.write(f'   Content-Length: {head_response.get("ContentLength")}')
                self.stdout.write(f'   ETag: {head_response.get("ETag")}')
            self.stdout.write(self.style.SUCCESS('   ✅ File exists in S3'))
        except s3_client.exceptions.NoSuchKey:
            raise CommandError('❌ File not found after upload - persistence issue!')
        except Exception as e:
            raise CommandError(f'❌ HEAD request failed: {e}')

        # Step 6: Download and verify content
        self.stdout.write('\n📋 Step 6: Downloading and verifying content...')
        try:
            start_time = time.time()
            get_response = s3_client.get_object(
                Bucket=s3_config['bucket_name'],
                Key=test_key
            )
            downloaded_content = get_response['Body'].read().decode('utf-8')
            download_time = time.time() - start_time

            if verbose:
                self.stdout.write(f'   Download time: {download_time:.3f}s')
                self.stdout.write(f'   Downloaded size: {len(downloaded_content)} bytes')

            if downloaded_content == test_content:
                self.stdout.write(self.style.SUCCESS('   ✅ Content integrity verified'))
            else:
                raise CommandError(
                    f'❌ Content mismatch!\n'
                    f'   Expected: {test_content[:50]}...\n'
                    f'   Got: {downloaded_content[:50]}...'
                )
        except Exception as e:
            if 'Content mismatch' in str(e):
                raise
            raise CommandError(f'❌ Download/verification failed: {e}')

        # Step 7: Delete test file (unless --keep-file)
        if not keep_file:
            self.stdout.write('\n📋 Step 7: Cleaning up test file...')
            try:
                start_time = time.time()
                s3_client.delete_object(
                    Bucket=s3_config['bucket_name'],
                    Key=test_key
                )
                delete_time = time.time() - start_time
                if verbose:
                    self.stdout.write(f'   Delete time: {delete_time:.3f}s')
                self.stdout.write(self.style.SUCCESS('   ✅ Test file deleted'))
            except Exception as e:
                self.stdout.write(self.style.WARNING(f'   ⚠️ Delete failed: {e}'))
        else:
            self.stdout.write(f'\n📋 Step 7: Skipping cleanup (--keep-file)')
            self.stdout.write(f'   Test file: s3://{s3_config["bucket_name"]}/{test_key}')

        # Summary
        self.stdout.write('\n' + '=' * 60)
        self.stdout.write(self.style.SUCCESS('🎉 S3 PERSISTENCE CHECK PASSED'))
        self.stdout.write('=' * 60)

        if verbose:
            self.stdout.write('\n📊 Performance Summary:')
            self.stdout.write(f'   Upload: {upload_time:.3f}s')
            self.stdout.write(f'   HEAD: {head_time:.3f}s')
            self.stdout.write(f'   Download: {download_time:.3f}s')
            if not keep_file:
                self.stdout.write(f'   Delete: {delete_time:.3f}s')

    def _load_s3_config(self):
        """Load S3 configuration from settings."""
        from mayan.apps.storage.settings import (
            setting_s3_enabled, setting_s3_endpoint_url, setting_s3_access_key,
            setting_s3_secret_key, setting_s3_bucket_name, setting_s3_region_name,
            setting_s3_use_ssl, setting_s3_verify
        )

        if not setting_s3_enabled.value:
            raise ValueError(
                'S3 storage is not enabled. Set STORAGE_S3_ENABLED=true'
            )

        config = {
            'endpoint_url': setting_s3_endpoint_url.value,
            'access_key': setting_s3_access_key.value,
            'secret_key': setting_s3_secret_key.value,
            'bucket_name': setting_s3_bucket_name.value,
            'region_name': setting_s3_region_name.value or 'ru-1',
            'use_ssl': setting_s3_use_ssl.value,
            'verify': setting_s3_verify.value,
        }

        # Validate required fields
        required = ['endpoint_url', 'access_key', 'secret_key', 'bucket_name']
        missing = [k for k in required if not config.get(k)]
        if missing:
            raise ValueError(f'Missing required S3 settings: {", ".join(missing)}')

        return config

    def _create_s3_client(self, config):
        """Create boto3 S3 client with Beget-compatible configuration."""
        import boto3
        from botocore.config import Config

        # Use s3v4 signature for better compatibility with Beget
        client_config = Config(
            s3={'addressing_style': 'path'},
            signature_version='s3v4',
            request_checksum_calculation='when_required'
        )

        return boto3.client(
            's3',
            aws_access_key_id=config['access_key'],
            aws_secret_access_key=config['secret_key'],
            endpoint_url=config['endpoint_url'],
            region_name=config['region_name'],
            use_ssl=config['use_ssl'],
            verify=config['verify'],
            config=client_config
        )

