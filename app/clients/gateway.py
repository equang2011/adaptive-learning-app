import logging
import os
import time
from typing import TypeVar

import httpx
from dotenv import load_dotenv
from pydantic import BaseModel, ValidationError

load_dotenv()

logger = logging.getLogger(__name__)

GATEWAY_URL = os.environ.get("GATEWAY_URL")
GATEWAY_API_KEY = os.environ.get("GATEWAY_API_KEY")

if not GATEWAY_URL or not GATEWAY_API_KEY:
    raise RuntimeError("GATEWAY_URL and GATEWAY_API_KEY must both be set")

RETRYABLE_STATUSES = {502, 504}
MAX_ATTEMPTS = 3
REQUEST_TIMEOUT = 90.0

HEADERS = {"Authorization": f"Bearer {GATEWAY_API_KEY}"}


class GatewayError(RuntimeError):
    """Raised when a gateway call fails for good (after any retries)."""


def call_gateway(model: str, messages: list[dict]) -> dict:
    last_error = "no attempts made"

    for attempt in range(MAX_ATTEMPTS):
        try:
            response = httpx.post(
                GATEWAY_URL,
                headers=HEADERS,
                json={"model": model, "messages": messages},
                timeout=REQUEST_TIMEOUT,
            )
        except httpx.TransportError as err:
            # Timeouts and connection failures: worth retrying.
            last_error = f"{type(err).__name__}: {err}"
        else:
            if response.status_code == 200:
                return response.json()
            if response.status_code not in RETRYABLE_STATUSES:
                # 400/401/403/422 etc.: retrying won't help.
                raise GatewayError(
                    f"Gateway returned {response.status_code}: {response.text}"
                )
            last_error = f"{response.status_code}: {response.text}"

        if attempt < MAX_ATTEMPTS - 1:
            time.sleep(2**attempt)  # 1s, then 2s

    raise GatewayError(f"Gateway call failed after {MAX_ATTEMPTS} attempts: {last_error}")


def invoke_gateway(model: str, prompt: str) -> str:
    """Send one user prompt and return only the model's text."""
    data = call_gateway(model, [{"role": "user", "content": prompt}])
    return data["content"]


T = TypeVar("T", bound=BaseModel)


def _strip_code_fence(text: str) -> str:
    text = text.strip()
    if text.startswith("```"):
        lines = text.splitlines()
        lines = lines[1:]  # drop the opening ``` or ```json line
        if lines and lines[-1].strip() == "```":
            lines = lines[:-1]
        text = "\n".join(lines).strip()
    return text


def invoke_gateway_validated(
    model: str,
    prompt: str,
    response_model: type[T],
    max_retries: int = 1,
) -> T:
    for attempt in range(max_retries + 1):
        content = invoke_gateway(model=model, prompt=prompt)
        try:
            return response_model.model_validate_json(_strip_code_fence(content))
        except ValidationError:
            if attempt == max_retries:
                raise
            logger.warning(
                "%s failed schema validation, retrying (attempt %d/%d)",
                response_model.__name__,
                attempt + 2,
                max_retries + 1,
            )