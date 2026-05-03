import requests

BASE_URL = "https://vera-bot-tp.onrender.com"

print("Checking bot health and metadata...")
health = requests.get(f"{BASE_URL}/v1/healthz").json()
print(f"Health: {health}")

metadata = requests.get(f"{BASE_URL}/v1/metadata").json()
print(f"\nMetadata: {metadata}")
print(f"\nModel: {metadata.get('model')}")
