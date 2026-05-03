"""Test LLM directly"""
from bot.llm_client import llm_client

print("Testing LLM client...")
response = llm_client.complete(
    "You are a helpful assistant.",
    "Say 'Hello World' in JSON format: {\"message\": \"...\"}"
)

if response:
    print(f"SUCCESS: {response}")
else:
    print("FAILED: No response from LLM")
