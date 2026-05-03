import requests
import json

BASE_URL = "https://vera-bot-tp.onrender.com"

# Send context first
print("Sending merchant context...")
merchant_ctx = {
    "scope": "merchant",
    "context_id": "M999",
    "version": 1,
    "payload": {
        "name": "Test Cafe",
        "owner_name": "John",
        "category_slug": "cafe",
        "locality": "Test Area",
        "rating": 4.5
    },
    "delivered_at": "2026-05-02T10:00:00Z"
}
r = requests.post(f"{BASE_URL}/v1/context", json=merchant_ctx)
print(f"Merchant context: {r.status_code}")

print("\nSending trigger context...")
trigger_ctx = {
    "scope": "trigger",
    "context_id": "T999",
    "version": 1,
    "payload": {
        "merchant_id": "M999",
        "type": "rating_drop",
        "data": {"current_rating": 4.2, "previous_rating": 4.5}
    },
    "delivered_at": "2026-05-02T10:01:00Z"
}
r = requests.post(f"{BASE_URL}/v1/context", json=trigger_ctx)
print(f"Trigger context: {r.status_code}")

print("\nCalling /v1/tick...")
tick_data = {
    "now": "2026-05-02T10:02:00Z",
    "available_triggers": ["T999"]
}

r = requests.post(f"{BASE_URL}/v1/tick", json=tick_data)
print(f"Status: {r.status_code}")
print(f"Response: {r.text}")

if r.status_code == 200:
    result = r.json()
    print(f"\nActions: {json.dumps(result, indent=2)}")
