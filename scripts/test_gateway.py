#!/usr/bin/env python3
"""Quick test script for Railway LLM gateway"""

from app.clients.gateway import invoke_gateway


try:
    response = invoke_gateway(
        model="nvidia/nemotron-3-ultra-550b-a55b:free",
        prompt="Say 'Hello from Railway!' and nothing else."
    )
    print("✓ Gateway working!")
    print(f"Response: {response}")
except Exception as e:
    print(f"✗ Gateway failed: {e}")
    import traceback
    traceback.print_exc()
