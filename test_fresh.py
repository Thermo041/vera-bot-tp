import requests
import json
import time
import random

BASE_URL = "https://vera-bot-tp.onrender.com"

# Use random IDs to avoid conflicts
merchant_id = f"M_{random.randint(10000, 99999)}"
trigger_id = f"T_{random.randint(10000, 99999)}"

print("=" * 60)
print(f"Testing with IDs: {merchant_id}, {trigger_id}")
print("=" * 60)

# Send merchant
print("\n1. Sending merchant...")
r = requests.post(f"{BASE_URL}/v1/context", json={
    "scope": "merchant",
    "context_id": merchant_id,
    "version": 1,
    "payload": {
        "name": "Fresh Dental Clinic",
        "owner_name": "Dr. Kumar",
        "category_slug": "dentists",
        "locality": "Indiranagar",
        "rating": 4.5
    },
    "delivered_at": "2026-05-03T10:00:00Z"
})
print(f"Status: {r.status_code}, Response: {r.json()}")

# Send trigger
print("\n2. Sending trigger...")
r = requests.post(f"{BASE_URL}/v1/context", json={
    "scope": "trigger",
    "context_id": trigger_id,
    "version": 1,
    "payload": {
        "merchant_id": merchant_id,
        "type": "rating_drop",
        "data": {"current_rating": 4.5, "previous_rating": 4.8}
    },
    "delivered_at": "2026-05-03T10:01:00Z"
})
print(f"Status: {r.status_code}, Response: {r.json()}")

# Call tick
print("\n3. Calling tick...")
time.sleep(1)
r = requests.post(f"{BASE_URL}/v1/tick", json={
    "now": "2026-05-03T10:02:00Z",
    "available_triggers": [trigger_id]
})
print(f"Status: {r.status_code}")
if r.status_code == 200:
    result = r.json()
    if result.get("actions"):
        print(f"SUCCESS! {len(result['actions'])} messages generated")
        print(f"Body: {result['actions'][0]['body'][:150]}...")
    else:
        print("FAILED: Empty actions - LLM likely failing")
else:
    print(f"❌ Error: {r.text}")
