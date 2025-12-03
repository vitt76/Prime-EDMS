#!/usr/bin/env python3
import requests

def test_integration():
    print("🧪 Testing Prime-EDMS Vite Proxy Integration")
    print("=" * 50)

    # 1. Check backend
    try:
        response = requests.get('http://localhost:8080/')
        if 'Mayan EDMS' in response.text:
            print("✅ Backend (Mayan EDMS) running on port 8080")
        else:
            print("❌ Backend not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to backend: {e}")
        return

    # 2. Check frontend
    try:
        response = requests.get('http://localhost:5173/')
        if len(response.text) > 100:
            print("✅ Frontend (Vue.js) running on port 5173")
        else:
            print("❌ Frontend not responding properly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to frontend: {e}")
        return

    # 3. Get admin credentials
    try:
        response = requests.get('http://localhost:8080/admin-credentials-js/')
        creds = response.json()
        username = creds.get('username')
        password = creds.get('password')

        if username and password:
            print(f"✅ Admin credentials retrieved: {username}")
        else:
            print("❌ No admin credentials available")
            return

    except Exception as e:
        print(f"❌ Cannot get admin credentials: {e}")
        return

    # 4. Test Vite proxy authentication
    print("🔐 Testing authentication via Vite proxy...")
    try:
        auth_response = requests.post(
            'http://localhost:5173/api/v4/auth/token/obtain/',
            json={'username': username, 'password': password},
            headers={'Content-Type': 'application/json'}
        )

        print(f"Vite proxy response: HTTP {auth_response.status_code}")

        if auth_response.status_code == 200:
            try:
                auth_data = auth_response.json()
                if 'token' in auth_data:
                    token = auth_data['token']
                    print("✅ Authentication successful via Vite proxy!")
                    print(f"Token: {token[:20]}...")
                    print("\n🎉 INTEGRATION TEST PASSED!")
                    print("Frontend ↔ Backend communication works!")
                else:
                    print("❌ No token in authentication response")
                    print(f"Response: {auth_data}")
            except:
                print("❌ Cannot parse authentication response as JSON")
                print(f"Raw response: {auth_response.text[:200]}")
        else:
            print(f"❌ Authentication failed with HTTP {auth_response.status_code}")
            print(f"Response: {auth_response.text[:200]}")

    except Exception as e:
        print(f"❌ Vite proxy test failed: {e}")

if __name__ == '__main__':
    test_integration()
