import requests
import urllib.parse
import json
import os
import boto3
import yaml











auth_token  = "YOUR_BEARER_TOKEN"  # Replace with your actual Bearer token







def get_agent_arn_from_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    default_agent = config.get('default_agent')
    if default_agent and default_agent in config.get('agents', {}):
        agent_config = config['agents'][default_agent]
        return agent_config.get('bedrock_agentcore', {}).get('agent_arn')
    
    return None

# Usage


# Configuration Constants
REGION_NAME = os.environ.get("REGION")  # Default to us-west-2 if not set

def stream_agent_response(prompt):
    # === Agent Invocation Demo ===
    yaml_file_path = ".bedrock_agentcore.yaml"  # Replace with your YAML file path
    invoke_agent_arn = get_agent_arn_from_yaml(yaml_file_path)
    print(f"Agent ARN: {invoke_agent_arn}")

    # auth_token = os.environ.get('TOKEN')  # Commented out for now
    print(f"Using Agent ARN: {invoke_agent_arn}")

    # URL encode the agent ARN
    escaped_agent_arn = urllib.parse.quote(invoke_agent_arn, safe='')

    # Construct the URL
    url = f"https://bedrock-agentcore.{REGION_NAME}.amazonaws.com/runtimes/{escaped_agent_arn}/invocations?qualifier=DEFAULT"

    # Get AWS credentials for signing
    session = boto3.Session()
    credentials = session.get_credentials()

    # Prepare request payload
    payload = json.dumps({"prompt": prompt})

    
    
    headers = {
        "Authorization": f"Bearer {auth_token}",  # Commented out Bearer token
        "X-Amzn-Trace-Id": "your-trace-id", 
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": "dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt"
    }

    # Create AWS request for signing
  

    # Enable verbose logging for requests (optional)
    # import logging
    # logging.basicConfig(level=logging.DEBUG)
    # logging.getLogger("urllib3.connectionpool").setLevel(logging.DEBUG)

    try:
        # Make streaming request
        with requests.post(
            url,
            headers=headers,
            data=payload,
            stream=True
        ) as invoke_response:
            
            print(f"Status Code: {invoke_response.status_code}")
            print(f"Response Headers: {dict(invoke_response.headers)}")
            
            # Handle response based on status code
            if invoke_response.status_code == 200:
                print("Agent Response (streaming):")
                
                # Process streaming response
                for line in invoke_response.iter_lines():
                    if line:  # skip keep-alive new lines
                        decoded_line = line.decode("utf-8")
                        
                        # Check for different streaming formats
                        if decoded_line.startswith("data:"):
                            try:
                                event = decoded_line[len("data: "):]
                                if event.strip() == "[DONE]":
                                    break
                                    
                                if '"message":' in event and '"text":' in event:
                                    # Extract just the assistant text content
                                    obj = json.loads(event)
                                    for c in obj.get("message", {}).get("content", []):
                                        if "text" in c:
                                            print(c["text"], end="", flush=True)
                                elif '"content":' in event or '"text":' in event:
                                    # Handle other streaming formats
                                    obj = json.loads(event)
                                    if 'content' in obj:
                                        print(obj['content'], end="", flush=True)
                                    elif 'text' in obj:
                                        print(obj['text'], end="", flush=True)
                            except json.JSONDecodeError:
                                # If not valid JSON, just print the event
                                if event.strip():
                                    print(event, end="", flush=True)
                        else:
                            # Handle non-SSE streaming format
                            try:
                                if decoded_line.strip():
                                    obj = json.loads(decoded_line)
                                    if isinstance(obj, dict):
                                        if 'content' in obj:
                                            print(obj['content'], end="", flush=True)
                                        elif 'text' in obj:
                                            print(obj['text'], end="", flush=True)
                                        else:
                                            print(json.dumps(obj, indent=2))
                                    else:
                                        print(obj, end="", flush=True)
                            except json.JSONDecodeError:
                                print(decoded_line, end="", flush=True)
                
                print()  # Add newline at the end
                
            elif invoke_response.status_code >= 400:
                print(f"Error Response ({invoke_response.status_code}):")
                try:
                    error_data = invoke_response.json()
                    print(json.dumps(error_data, indent=2))
                except:
                    print(invoke_response.text)
            else:
                print(f"Unexpected status code: {invoke_response.status_code}")
                print("Response text:")
                print(invoke_response.text[:500])
                
    except Exception as e:
        print(f"Error making request: {str(e)}")

# Example usage
if __name__ == "__main__":
    stream_agent_response("give me famous places near seattle")