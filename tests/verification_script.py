#!/usr/bin/env python3
"""
API Verification Script for Mayan EDMS
Tests authentication, password change, and upload endpoints
"""

import requests
import json

# Configuration
BASE_URL = "http://127.0.0.1:8080"
HEADERS = {
    'Content-Type': 'application/json',
    'Accept': 'application/json'
}

def test_authentication():
    """Test 1: Get authentication token"""
    print("\n" + "="*50)
    print("TEST 1: AUTHENTICATION - Get Token")
    print("="*50)

    url = f"{BASE_URL}/api/v4/auth/token/obtain/"
    payload = {
        "username": "admin",
        "password": "admin123"
    }

    print(f"URL: {url}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=HEADERS, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
            return response_json if 'access' in response_json else None
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")
            return None

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")
        return None

def test_password_change(token):
    """Test 2: Password change endpoint"""
    print("\n" + "="*50)
    print("TEST 2: PASSWORD CHANGE - POST /api/v4/users/current/password/")
    print("="*50)

    url = f"{BASE_URL}/api/v4/users/current/password/"
    payload = {
        "new_password": "newpassword123"
    }

    headers = HEADERS.copy()
    if token:
        headers['Authorization'] = f"Token {token}"

    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def test_upload_initiation(token):
    """Test 3: Upload initiation"""
    print("\n" + "="*50)
    print("TEST 3: UPLOAD INITIATION - POST /api/v4/uploads/init/")
    print("="*50)

    url = f"{BASE_URL}/api/v4/uploads/init/"
    payload = {
        "filename": "test_document.pdf",
        "total_size": 1024000,
        "content_type": "application/pdf",
        "document_type_id": 1
    }

    headers = HEADERS.copy()
    if token:
        headers['Authorization'] = f"Token {token}"

    print(f"URL: {url}")
    print(f"Headers: {headers}")
    print(f"Payload: {json.dumps(payload, indent=2)}")

    try:
        response = requests.post(url, json=payload, headers=headers, timeout=10)
        print(f"Status Code: {response.status_code}")
        print(f"Response Headers: {dict(response.headers)}")

        try:
            response_json = response.json()
            print(f"Response JSON: {json.dumps(response_json, indent=2)}")
        except json.JSONDecodeError:
            print(f"Response Text: {response.text}")

    except requests.exceptions.RequestException as e:
        print(f"Request failed: {e}")

def main():
    """Main test execution"""
    print("Mayan EDMS API Verification Script")
    print(f"Target: {BASE_URL}")
    print("Testing 3 critical endpoints...")

    # Test 1: Authentication
    token = test_authentication()

    # Test 2: Password Change
    test_password_change(token)

    # Test 3: Upload Initiation
    test_upload_initiation(token)

    print("\n" + "="*50)
    print("VERIFICATION COMPLETE")
    print("="*50)

if __name__ == "__main__":
    main()
