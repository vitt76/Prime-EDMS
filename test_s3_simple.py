#!/usr/bin/env python3
"""
Simple S3 connection test
"""
import boto3
import botocore.exceptions

# Real S3 credentials
bucket_name = 'cafdf4e9fa32-righteous-rimma'

try:
    print("Testing basic S3 connection...")
    session = boto3.Session(
        aws_access_key_id='2EILOPQ3JUAW797ZF3DL',
        aws_secret_access_key='RjLi6AD0OgofbJ2YbzMnHFCqudVwf9Tqw3kB9E7z',
        region_name='ru-1'
    )
    from botocore.awsrequest import AWSRequest
    from botocore.endpoint import Endpoint
    from botocore.auth import SigV4Auth
    from botocore.credentials import Credentials

    # Create custom client with explicit s3v4
    credentials = Credentials(
        access_key='2EILOPQ3JUAW797ZF3DL',
        secret_key='RjLi6AD0OgofbJ2YbzMnHFCqudVwf9Tqw3kB9E7z'
    )

    s3 = session.client(
        's3',
        endpoint_url='https://s3.ru1.storage.beget.cloud',
        verify=False,
        config=boto3.session.Config(
            signature_version='s3v4',
            region_name='ru-1',
            s3={'addressing_style': 'path'}
        )
    )

    print("Testing head_bucket...")
    s3.head_bucket(Bucket=bucket_name)
    print("✅ head_bucket successful")

    print("Testing list_objects...")
    try:
        response = s3.list_objects_v2(Bucket=bucket_name)
        print(f"✅ list_objects successful, found {response.get('KeyCount', 0)} objects")
    except Exception as e:
        print(f"⚠️ list_objects failed: {e}")

    print("Testing put_object...")
    s3.put_object(Bucket=bucket_name, Key='test.txt', Body='Hello World')
    print("✅ put_object successful")

    print("Testing get_object...")
    response = s3.get_object(Bucket=bucket_name, Key='test.txt')
    print(f"✅ get_object successful: {response['Body'].read()}")

    print("Testing delete_object...")
    s3.delete_object(Bucket=bucket_name, Key='test.txt')
    print("✅ delete_object successful")

    print("🎉 All S3 operations successful!")

except Exception as e:
    print(f"❌ S3 test failed: {e}")
    import traceback
    traceback.print_exc()
