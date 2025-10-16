#!/usr/bin/env python3

import requests
import json

BASE_URL = "http://localhost:80"

def test_api():
    print("🧪 Testing Distribution Portal API...")

    # Test basic API
    try:
        response = requests.get(f"{BASE_URL}/api/v4/test/", headers={'Accept': 'application/json'})
        if response.status_code == 200:
            print("✅ API test endpoint works:", response.json())
        else:
            print("❌ API test failed:", response.status_code)
            return
    except Exception as e:
        print("❌ API connection failed:", e)
        return

    # Test rendition presets
    try:
        response = requests.get(f"{BASE_URL}/api/v4/rendition_presets/", headers={'Accept': 'application/json'})
        print("📋 Rendition presets:", len(response.json()['results']), "found")
    except Exception as e:
        print("❌ Rendition presets API failed:", e)

    # Test portal access (should return 404 for invalid token)
    try:
        response = requests.get(f"{BASE_URL}/publish/invalid-token/")
        if response.status_code == 404:
            print("✅ Portal correctly returns 404 for invalid token")
        else:
            print("⚠️ Portal returned:", response.status_code)
    except Exception as e:
        print("❌ Portal test failed:", e)

if __name__ == '__main__':
    test_api()
