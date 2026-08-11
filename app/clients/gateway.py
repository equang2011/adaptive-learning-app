import os

import httpx
from dotenv import load_dotenv

load_dotenv()

gateway_api_key = os.getenv("LLM_GATEWAY_API_KEY")

headers = {
    "Authorization": f"Bearer {gateway_api_key}",
}


def invoke_gateway(
    model: str,
    prompt: str,
) -> str:
    # Call POST /invoke
    # Handle gateway/network failure
    # Return only the normalized content string

    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    try:
        response = httpx.post(
            "https://llm-gateway-production-b085.up.railway.app/invoke",
            json=payload,
            headers=headers,
            timeout=550.0,
        )
    except httpx.RequestError as err:
        raise RuntimeError("Gateway request failed") from err

    if response.status_code != 200:
        raise RuntimeError(f"Gateway returned {response.status_code}: {response.text}")

    data = response.json()
    return data["content"]
