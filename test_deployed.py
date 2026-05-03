import requests
import json

BASE_URL = "https://vera-bot-tp.onrender.com"

print("=" * 60)
print("TESTING DEPLOYED VERA BOT")
print("=" * 60)

# Test 1: Health Check
print("\n1. Testing /v1/healthz...")
response = requests.get(f"{BASE_URL}/v1/healthz")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 2: Metadata
print("\n2. Testing /v1/metadata...")
response = requests.get(f"{BASE_URL}/v1/metadata")
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 3: Send Context
print("\n3. Testing /v1/context...")
context_data = {
    "scope": "merchant",
    "context_id": "M123",
    "version": 1,
    "payload": {
        "name": "Cafe Delight",
        "owner_name": "Priya Sharma",
        "category": "cafe",
        "locality": "Koramangala",
        "rating": 4.5,
        "total_reviews": 230,
        "offers": ["20% off on beverages", "Free dessert with main course"]
    },
    "delivered_at": "2026-05-02T10:00:00Z"
}

response = requests.post(f"{BASE_URL}/v1/context", json=context_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 4: Send Trigger Context
print("\n4. Testing /v1/context (trigger)...")
trigger_data = {
    "scope": "trigger",
    "context_id": "T123",
    "version": 1,
    "payload": {
        "merchant_id": "M123",
        "type": "rating_drop",
        "data": {
            "current_rating": 4.2,
            "previous_rating": 4.5,
            "drop_percentage": 6.7
        }
    },
    "delivered_at": "2026-05-02T10:01:00Z"
}

response = requests.post(f"{BASE_URL}/v1/context", json=trigger_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

# Test 5: Generate Message (Tick)
print("\n5. Testing /v1/tick (Message Generation)...")
tick_data = {
    "now": "2026-05-02T10:02:00Z",
    "available_triggers": ["T123"]
}

response = requests.post(f"{BASE_URL}/v1/tick", json=tick_data)
print(f"Status: {response.status_code}")
print(f"Response: {json.dumps(response.json(), indent=2)}")

if response.status_code == 200:
    result = response.json()
    actions = result.get("actions", [])
    if actions:
        print(f"\n[SUCCESS] {len(actions)} MESSAGE(S) GENERATED:")
        for i, action in enumerate(actions, 1):
            print(f"\n--- Message {i} ---")
            print(f"Conversation ID: {action.get('conversation_id')}")
            print(f"Body: {action.get('body')}")
    else:
        print("\n[INFO] No messages generated")

print("\n" + "=" * 60)
print("TESTING COMPLETE!")
print("=" * 60)
