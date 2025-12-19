#!/usr/bin/env python3
"""
Test script for Prime-EDMS backend API integration
"""

import requests
import json

def test_backend_api():
    print("🧪 Testing Prime-EDMS Backend API Integration")
    print("=" * 50)

    base_url = "http://localhost:8080"

    # Test 1: Check if backend is running
    print("1. Testing backend availability...")
    try:
        response = requests.get(f"{base_url}/")
        if response.status_code == 200:
            print("✅ Backend is running")
        else:
            print(f"❌ Backend returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return False

    # Test 2: Check login page has JavaScript injection
    print("2. Testing login page JavaScript injection...")
    try:
        response = requests.get(f"{base_url}/authentication/login/")
        if "Prime-EDMS Frontend Integration" in response.text:
            print("✅ JavaScript injection found on login page")
        else:
            print("❌ JavaScript injection not found")
            return False
    except Exception as e:
        print(f"❌ Cannot access login page: {e}")
        return False

    # Test 3: Test API endpoint
    print("3. Testing autoadmin credentials API...")
    try:
        response = requests.get(f"{base_url}/admin-credentials-js/")
        if response.status_code == 200:
            data = response.json()
            print("✅ API endpoint responds")
            print(f"   Auto-generated: {data.get('is_auto_generated', 'N/A')}")
            if data.get('is_auto_generated'):
                print(f"   Username: {data.get('username', 'N/A')}")
                print(f"   Email: {data.get('email', 'N/A')}")
                print(f"   Password: {'*' * len(data.get('password', ''))}")
        else:
            print(f"❌ API returned status {response.status_code}")
            return False
    except Exception as e:
        print(f"❌ API call failed: {e}")
        return False

    print("\n🎉 All backend tests passed!")
    return True

if __name__ == "__main__":
    test_backend_api()


