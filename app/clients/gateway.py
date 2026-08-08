
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
                timeout=210.0,
            )
    except httpx.RequestError as err:
        print(f"Request failed: {err}")
        return

    if response.status_code != 200:
        print(response.status_code, response.text)
        return

    data = response.json()
    return data["content"]


    
