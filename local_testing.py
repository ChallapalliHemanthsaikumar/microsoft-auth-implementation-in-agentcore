

import requests

def stream_local_agent(prompt):
    url = "http://localhost:8080/invocations"
    headers = {"Content-Type": "application/json"}
    payload = {"prompt": prompt}

    with requests.post(url, headers=headers, json=payload, stream=True) as response:
        if response.status_code != 200:
            print(f"Error {response.status_code}: {response.text}")
            return

        for line in response.iter_lines():
            if line:  # skip keep-alive new lines
                decoded_line = line.decode("utf-8")

                # Only pick out assistant's content
                if decoded_line.startswith("data:"):
                    try:
                        event = decoded_line[len("data: "):]
                        if '"message":' in event and '"text":' in event:
                            # Extract just the assistant text content
                            import json
                            obj = json.loads(event)
                            for c in obj.get("message", {}).get("content", []):
                                if "text" in c:
                                    print(c["text"], end="", flush=True)
                    except Exception:
                        pass

# Example usage
if __name__ == "__main__":
    stream_local_agent("give me famous places near seattle")
