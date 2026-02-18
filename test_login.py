import requests
import json

# Test login endpoint
url = "http://localhost:8000/api/v1/auth/login"
credentials = {
    "email": "raj.kumar@bank.com",
    "password": "password123"
}

print("Testing login endpoint...")
print(f"URL: {url}")
print(f"Credentials: {json.dumps(credentials, indent=2)}")
print("-" * 50)

try:
    response = requests.post(url, json=credentials)
    print(f"Status Code: {response.status_code}")
    print(f"Response Headers: {dict(response.headers)}")
    print(f"Response Body: {response.text}")
    
    if response.status_code == 200:
        print("\n✅ Login successful!")
        data = response.json()
        print(f"Token: {data.get('token', 'N/A')[:50]}...")
        print(f"Banker: {data.get('banker_name', 'N/A')}")
    else:
        print(f"\n❌ Login failed with status {response.status_code}")
        try:
            error_data = response.json()
            print(f"Error detail: {error_data.get('detail', 'No detail provided')}")
        except:
            print(f"Raw error: {response.text}")
            
except Exception as e:
    print(f"\n❌ Request failed: {e}")
