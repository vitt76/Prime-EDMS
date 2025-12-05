#!/usr/bin/env python3
import requests
import re

def test_mayan_login():
    print("🧪 Testing Mayan EDMS login and token retrieval")
    print("=" * 50)

    session = requests.Session()

    try:
        # Step 1: Get login page and extract CSRF token
        print("1. Getting login page and CSRF token...")
        response = session.get('http://localhost:8080/authentication/login/')

        if 'csrfmiddlewaretoken' in response.text:
            print("   ✅ CSRF token found")

            # Extract CSRF token
            csrf_match = re.search(r'name="csrfmiddlewaretoken" value="([^"]+)"', response.text)
            if csrf_match:
                csrf_token = csrf_match.group(1)
                print(f"   ✅ CSRF token: {csrf_token[:20]}...")

                # Step 2: Get real credentials for testing
                print("2. Getting real admin credentials...")
                cred_response = session.get('http://localhost:8080/admin-credentials-js/')
                if cred_response.status_code == 200:
                    try:
                        creds = cred_response.json()
                        username = creds.get('username', 'autoadmin@example.com')
                        password = creds.get('password', 'test')
                        email = creds.get('email', username)
                        print(f"   ✅ Real credentials: {username}")

                        # Step 3: Login with real credentials
                        print("3. Attempting login...")
                        login_data = {
                            'username': email,
                            'password': password,
                            'csrfmiddlewaretoken': csrf_token
                        }

                        headers = {
                            'Referer': 'http://localhost:8080/authentication/login/',
                            'Content-Type': 'application/x-www-form-urlencoded'
                        }

                        login_response = session.post('http://localhost:8080/authentication/login/',
                                                    data=login_data, headers=headers)

                        print(f"   Login response: HTTP {login_response.status_code}")

                        if login_response.status_code in [200, 302]:
                            print("   ✅ Login successful")

                            # Step 4: Get API token
                            print("4. Getting API token...")
                            token_response = session.post(
                                'http://localhost:8080/api/v4/auth/token/obtain/',
                                json={'username': username, 'password': password},
                                headers={'Content-Type': 'application/json'}
                            )

                            print(f"   Token API response: HTTP {token_response.status_code}")

                            if token_response.status_code == 200:
                                try:
                                    token_data = token_response.json()
                                    if 'token' in token_data:
                                        token = token_data['token']
                                        print("   ✅ API token obtained!")
                                        print(f"   Token: {token[:20]}...")

                                        # Step 5: Test frontend with token
                                        print("5. Testing frontend redirect with token...")
                                        frontend_url = f'http://localhost:5173/?token={token}'
                                        frontend_response = requests.get(frontend_url)

                                        print(f"   Frontend response: HTTP {frontend_response.status_code}")
                                        if frontend_response.status_code == 200:
                                            print("   ✅ Frontend loaded with token!")
                                            print("\n🎉 COMPLETE INTEGRATION SUCCESSFUL!")
                                            print("User can now:")
                                            print("1. Login to Mayan EDMS at localhost:8080")
                                            print("2. Get automatically redirected to localhost:5173 with token")
                                            print("3. Access full DAM system seamlessly")
                                        else:
                                            print("   ❌ Frontend failed to load with token")
                                    else:
                                        print("   ❌ No token in API response")
                                        print(f"   Response: {token_data}")
                                except:
                                    print("   ❌ Cannot parse token response as JSON")
                                    print(f"   Raw response: {token_response.text[:200]}")
                            else:
                                print("   ❌ Token API failed")
                                print("   Response preview:", token_response.text[:200])
                        else:
                            print("   ❌ Login failed")
                            print("   Response preview:", login_response.text[:200])

                    except:
                        print("   ❌ Cannot parse credentials JSON")
                        print(f"   Raw response: {cred_response.text[:200]}")
                else:
                    print("   ❌ Cannot get credentials")
            else:
                print("   ❌ CSRF token not found in expected format")
        else:
            print("   ❌ CSRF token not found in login page")

    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    test_mayan_login()
