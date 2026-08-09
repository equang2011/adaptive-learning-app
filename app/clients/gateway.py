
import httpx




def invoke_gateway(
    model: str,
    prompt: str,
) -> str:
    # Call POST /invoke
    # Handle gateway/network failure
    # Return only the normalized content string
    

    payload = {
        "model": model,
        "messages" : [
            {
                "role": "user",
                "content": prompt}
        ]
    }

    try:
        response = httpx.post(
            "http://127.0.0.1:8000/invoke",
            json=payload,
            timeout=550.0,
        )
    except httpx.RequestError as err:
        raise RuntimeError("Gateway request failed") from err

    if response.status_code != 200:
        raise RuntimeError(
            f"Gateway returned {response.status_code}: {response.text}"
        )

    data = response.json()
    return data["content"]


    
