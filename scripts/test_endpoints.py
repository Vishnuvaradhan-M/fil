
import requests
import time
import sys

BASE_URL = "http://127.0.0.1:8000"

def wait_for_server(retries=10, delay=2):
    print("Waiting for server to start...")
    for i in range(retries):
        try:
            response = requests.get(f"{BASE_URL}/")
            if response.status_code == 200:
                print("Server is up!")
                return True
        except requests.ConnectionError:
            pass
        time.sleep(delay)
    print("Server failed to start.")
    return False

def test_endpoints():
    print("\nXXX Testing Endpoints XXX")
    
    # 1. Test Root
    try:
        resp = requests.get(f"{BASE_URL}/")
        print(f"GET / : {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"GET / FAILED: {e}")

    # 2. Test General Health
    try:
        resp = requests.get(f"{BASE_URL}/health")
        print(f"GET /health : {resp.status_code} - {resp.json()}")
    except Exception as e:
        print(f"GET /health FAILED: {e}")

    # 3. Test DB Health (The core migration feature)
    try:
        resp = requests.get(f"{BASE_URL}/api/v1/health/db")
        print(f"GET /api/v1/health/db : {resp.status_code} - {resp.json()}")
        if resp.status_code == 200 and resp.json().get("status") == "db_connected":
            print(">>> DB HEALTH CHECK PASSED <<<")
        else:
            print(">>> DB HEALTH CHECK FAILED <<<")
    except Exception as e:
        print(f"GET /api/v1/health/db FAILED: {e}")

if __name__ == "__main__":
    if wait_for_server():
        test_endpoints()
    else:
        sys.exit(1)
