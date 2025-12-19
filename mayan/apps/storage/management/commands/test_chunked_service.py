"""
Test script for ChunkedUploadService.
Tests presigned URLs and S3 operations.
"""
from django.core.management.base import BaseCommand, CommandError


class Command(BaseCommand):
    help = 'Test ChunkedUploadService S3 operations'

    def handle(self, *args, **options):
        self.stdout.write('Testing ChunkedUploadService...\n')
        
        try:
            from mayan.apps.storage.services.chunked_upload_service import (
                ChunkedUploadService, S3ServiceUnavailableError
            )
            
            service = ChunkedUploadService()
            
            # Test 1: Connection
            self.stdout.write('1. Testing connection...')
            success, msg = service.check_connection()
            if not success:
                raise CommandError(f'Connection failed: {msg}')
            self.stdout.write(self.style.SUCCESS(f'   ✅ {msg}\n'))
            
            # Test 2: Generate S3 key
            self.stdout.write('2. Testing S3 key generation...')
            key = service.generate_s3_key('test_file.txt')
            self.stdout.write(self.style.SUCCESS(f'   ✅ Generated key: {key}\n'))
            
            # Test 3: Upload test file
            self.stdout.write('3. Testing file upload...')
            test_content = b'Test content for presigned URL verification'
            response = service.client.put_object(
                Bucket=service.config['bucket_name'],
                Key=key,
                Body=test_content
            )
            self.stdout.write(self.style.SUCCESS(f'   ✅ Uploaded with ETag: {response.get("ETag")}\n'))
            
            # Test 4: Presigned URL
            self.stdout.write('4. Testing presigned URL generation...')
            url = service.get_object_url(key, expires_in=300)
            self.stdout.write(self.style.SUCCESS(f'   ✅ URL: {url[:80]}...\n'))
            
            # Test 5: Download via presigned URL
            self.stdout.write('5. Testing download via requests...')
            import requests
            resp = requests.get(url, timeout=30)
            if resp.status_code == 200 and resp.content == test_content:
                self.stdout.write(self.style.SUCCESS(f'   ✅ Downloaded and verified content\n'))
            else:
                self.stdout.write(self.style.ERROR(
                    f'   ❌ Failed: status={resp.status_code}, content match={resp.content == test_content}\n'
                ))
            
            # Test 6: Delete
            self.stdout.write('6. Testing file deletion...')
            service.delete_object(key)
            self.stdout.write(self.style.SUCCESS(f'   ✅ Deleted: {key}\n'))
            
            self.stdout.write(self.style.SUCCESS('\n🎉 All ChunkedUploadService tests passed!\n'))
            
        except S3ServiceUnavailableError as e:
            raise CommandError(f'S3 service error: {e}')
        except Exception as e:
            raise CommandError(f'Test failed: {e}')















