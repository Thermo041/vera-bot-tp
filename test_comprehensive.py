import requests
import json
import time

BASE_URL = "https://vera-bot-tp.onrender.com"

print("=" * 60)
print("COMPREHENSIVE BOT TEST")
print("=" * 60)

# Step 1: Send merchant context
print("\n1. Sending merchant context...")
merchant = {
    "scope": "merchant",
    "context_id": "M_TEST_001",
    "version": 1,
    "payload": {
        "name": "Test Dental Clinic",
        "owner_name": "Dr. Sharma",
        "category_slug": "dentists",
        "locality": "Koramangala",
        "rating": 4.3,
        "total_reviews": 150,
        "offers": ["20% off on teeth cleaning"]
    },
    "delivered_at": "2026-05-03T10:00:00Z"
}
r = requests.post(f"{BASE_URL}/v1/context", json=merchant)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Step 2: Send trigger context
print("\n2. Sending trigger context...")
trigger = {
    "scope": "trigger",
    "context_id": "T_TEST_001",
    "version": 1,
    "payload": {
        "merchant_id": "M_TEST_001",
        "type": "rating_drop",
        "data": {
            "current_rating": 4.3,
            "previous_rating": 4.7,
            "drop_percentage": 8.5,
            "recent_negative_reviews": 3
        }
    },
    "delivered_at": "2026-05-03T10:01:00Z"
}
r = requests.post(f"{BASE_URL}/v1/context", json=trigger)
print(f"   Status: {r.status_code}")
print(f"   Response: {r.json()}")

# Step 3: Call tick
print("\n3. Calling /v1/tick...")
time.sleep(1)  # Give it a moment
tick = {
    "now": "2026-05-03T10:02:00Z",
    "available_triggers": ["T_TEST_001"]
}
r = requests.post(f"{BASE_URL}/v1/tick", json=tick)
print(f"   Status: {r.status_code}")

if r.status_code == 200:
    result = r.json()
    print(f"   Response: {json.dumps(result, indent=2)}")
    
    if result.get("actions"):
        print(f"\n✅ SUCCESS! Generated {len(result['actions'])} message(s)")
        for action in result["actions"]:
            print(f"\n   Message Body: {action.get('body')[:200]}...")
            print(f"   CTA: {action.get('cta')}")
            print(f"   Rationale: {action.get('rationale')}")
    else:
        print("\n❌ FAILED: Empty actions array")
        print("   This means compose_message() returned None")
        print("   Check Render logs for LLM errors")
else:
    print(f"   Error: {r.text}")

print("\n" + "=" * 60)
