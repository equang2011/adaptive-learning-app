import os
from typing import TypeVar

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

gateway_api_key = os.getenv("LLM_GATEWAY_API_KEY")

headers = {
    "Authorization": f"Bearer {gateway_api_key}",
}

PROD_URL ="https://llm-gateway-production-b085.up.railway.app/invoke"
LOCAL_URL = "http://127.0.0.1:8000/invoke"


def invoke_gateway(
    model: str,
    prompt: str,
) -> str:
    # Call POST /invoke
    # Handle gateway/network failure
    # Return only the normalized content string

    payload = {"model": model, "messages": [{"role": "user", "content": prompt}]}

    try:
        # TODO: switch back to PROD_URL when done with local batch testing
        response = httpx.post(
            LOCAL_URL,
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


T = TypeVar("T", bound=BaseModel)


def invoke_gateway_validated(
    model: str,
    prompt: str,
    response_model: type[T],
    max_retries: int = 1,
) -> T:
    for attempt in range(max_retries + 1):
        content = invoke_gateway(model=model, prompt=prompt)
        try:
            return response_model.model_validate_json(content)
        except ValidationError:
            if attempt == max_retries:
                raise
            print(
                f"{response_model.__name__} failed schema validation, "
                f"retrying (attempt {attempt + 2}/{max_retries + 1})..."
            )
