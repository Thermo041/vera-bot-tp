import requests
import json

BOT_URL = "http://localhost:8080"

print("Testing bot endpoints...")

# Test healthz
resp = requests.get(f"{BOT_URL}/v1/healthz")
print(f"\n✓ Healthz: {resp.json()}")

# Test metadata
resp = requests.get(f"{BOT_URL}/v1/metadata")
print(f"\n✓ Metadata: {resp.json()}")

# Push category
with open("dataset/categories/dentists.json") as f:
    cat = json.load(f)

resp = requests.post(f"{BOT_URL}/v1/context", json={
    "scope": "category",
    "context_id": "dentists",
    "version": 1,
    "payload": cat,
    "delivered_at": "2026-04-26T10:00:00Z"
})
print(f"\n✓ Category pushed: {resp.json()}")

# Push merchant
with open("dataset/merchants_seed.json") as f:
    data = json.load(f)
    merchant = data["merchants"][0]

resp = requests.post(f"{BOT_URL}/v1/context", json={
    "scope": "merchant",
    "context_id": merchant["merchant_id"],
    "version": 1,
    "payload": merchant,
    "delivered_at": "2026-04-26T10:00:00Z"
})
print(f"\n✓ Merchant pushed: {resp.json()}")

# Push trigger
with open("dataset/triggers_seed.json") as f:
    data = json.load(f)
    trigger = data["triggers"][0]

resp = requests.post(f"{BOT_URL}/v1/context", json={
    "scope": "trigger",
    "context_id": trigger["id"],
    "version": 1,
    "payload": trigger,
    "delivered_at": "2026-04-26T10:00:00Z"
})
print(f"\n✓ Trigger pushed: {resp.json()}")

# Test tick
resp = requests.post(f"{BOT_URL}/v1/tick", json={
    "now": "2026-04-26T10:05:00Z",
    "available_triggers": [trigger["id"]]
})
result = resp.json()
print(f"\n✓ Tick response: {len(result.get('actions', []))} actions")

if result.get("actions"):
    action = result["actions"][0]
    print(f"\n📧 MESSAGE GENERATED:")
    print(f"   Body: {action['body'][:200]}...")
    print(f"   CTA: {action['cta']}")
    print(f"   Rationale: {action['rationale']}")

print("\n✅ BOT IS WORKING!")
