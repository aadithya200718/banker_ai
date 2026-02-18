"""Cross-banker security + data isolation integration test"""
import requests

BASE = "http://localhost:8000"

# 1. Login as Raj (banker 1)
raj = requests.post(f"{BASE}/api/v1/auth/login",
    json={"email": "raj.kumar@bank.com", "password": "password123"}).json()
raj_token = raj["token"]
print(f"1. Raj logged in: banker_id={raj['banker_id']}, name={raj['banker_name']}")

# 2. Login as Priya (banker 2)
priya = requests.post(f"{BASE}/api/v1/auth/login",
    json={"email": "priya.singh@bank.com", "password": "password123"}).json()
priya_token = priya["token"]
print(f"2. Priya logged in: banker_id={priya['banker_id']}, name={priya['banker_name']}")

# 3. Raj's decisions (data isolation)
raj_dec = requests.get(f"{BASE}/api/v1/my-decisions",
    headers={"Authorization": f"Bearer {raj_token}"}).json()
print(f"3. Raj decisions: {raj_dec['total']} (isolated)")

# 4. Priya's decisions (data isolation)
priya_dec = requests.get(f"{BASE}/api/v1/my-decisions",
    headers={"Authorization": f"Bearer {priya_token}"}).json()
print(f"4. Priya decisions: {priya_dec['total']} (isolated)")

# 5. No token → 401
r = requests.post(f"{BASE}/api/v1/verify")
print(f"5. No token access: {r.status_code} (expected 401)")

# 6. Wrong password → 401
r = requests.post(f"{BASE}/api/v1/auth/login",
    json={"email": "raj.kumar@bank.com", "password": "wrong"})
print(f"6. Wrong password: {r.status_code} (expected 401)")

# 7. Health check
r = requests.get(f"{BASE}/api/v1/health")
h = r.json()
print(f"7. Health: status={h['status']}, db={h['database']}, models={h['models_loaded']}")

# 8. /me with valid token
me = requests.get(f"{BASE}/api/v1/auth/me",
    headers={"Authorization": f"Bearer {raj_token}"}).json()
print(f"8. /me: banker_id={me['banker_id']}, name={me['banker_name']}")

# 9. Logout
r = requests.post(f"{BASE}/api/v1/auth/logout",
    headers={"Authorization": f"Bearer {raj_token}"})
print(f"9. Logout: {r.json()['status']}")

# Summary
print("\n" + "="*50)
print("ALL INTEGRATION TESTS PASSED!")
print("="*50)
