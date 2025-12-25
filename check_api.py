#!/usr/bin/env python3
import requests

def check_api():
    # Check backend
    try:
        response = requests.get('http://localhost:8080/')
        if 'Mayan EDMS' in response.text:
            print('✅ Backend (Mayan EDMS) is running')
        else:
            print('❌ Backend not responding properly')
            return
    except Exception as e:
        print('❌ Cannot connect to backend:', e)
        return

    # Get admin credentials
    try:
        response = requests.get('http://localhost:8080/admin-credentials-js/')
        data = response.json()
        print('✅ Admin credentials retrieved:')
        print(f'Username: {data.get("username", "N/A")}')
        print(f'Email: {data.get("email", "N/A")}')
        print(f'Password: {data.get("password", "N/A")}')
        print(f'Auto-generated: {data.get("is_auto_generated", False)}')

        # Test authentication
        username = data.get('username')
        password = data.get('password')
        if username and password:
            auth_response = requests.post(
                'http://localhost:8080/api/v4/auth/token/obtain/',
                json={'username': username, 'password': password},
                headers={'Content-Type': 'application/json'}
            )
            if auth_response.status_code == 200:
                auth_data = auth_response.json()
                if 'token' in auth_data:
                    print('✅ Authentication successful!')
                    print(f'Token: {auth_data["token"][:20]}...')
                else:
                    print('❌ Authentication failed - no token')
                    print('Response:', auth_data)
            else:
                print(f'❌ Authentication failed - HTTP {auth_response.status_code}')
                print('Response:', auth_response.text[:200])

    except Exception as e:
        print('❌ API error:', e)

if __name__ == '__main__':
    check_api()




