import streamlit as st
import requests
import urllib.parse
import json
import os
import base64
import secrets
from dotenv import load_dotenv
import time
import yaml
# Load environment variables
load_dotenv()

# Configuration from .env
CLIENT_ID = os.getenv('CLIENT_ID')
CLIENT_SECRET = os.getenv('CLIENT_SECRET')
TENANT_ID = os.getenv('TENANT_ID', 'common')
AUTHORITY = os.getenv('AUTHORITY')
REDIRECT_URI = os.getenv('REDIRECT_URI') # Streamlit default

SCOPE = os.getenv('SCOPE')
# Agent Configuration

def get_agent_arn_from_yaml(yaml_file_path):
    with open(yaml_file_path, 'r') as file:
        config = yaml.safe_load(file)
    
    default_agent = config.get('default_agent')
    if default_agent and default_agent in config.get('agents', {}):
        agent_config = config['agents'][default_agent]
        return agent_config.get('bedrock_agentcore', {}).get('agent_arn')
    
    return None


yaml_file_path = ".bedrock_agentcore.yaml"  # Replace with your YAML file path
AGENT_ARN = get_agent_arn_from_yaml(yaml_file_path)





AWS_REGION = os.getenv('AWS_REGION')

# Microsoft Graph scopes
SCOPES = ["openid", "profile", "email",SCOPE]

def get_auth_url():
    """Generate Microsoft OAuth2 authorization URL"""
    state = secrets.token_urlsafe(32)
    # Store state in URL parameter instead of session state for persistence
    
    params = {
        'client_id': CLIENT_ID,
        'response_type': 'code',
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES),
        'state': state,
        'response_mode': 'query'
    }
    
    auth_url = f"{AUTHORITY}/oauth2/v2.0/authorize?" + urllib.parse.urlencode(params)
    return auth_url, state

def exchange_code_for_token(authorization_code, state, original_state):
    """Exchange authorization code for access token"""
    # More flexible state validation - allow if states match or if original_state is provided
    if state != original_state and original_state is not None:
        st.error(f"Invalid state parameter. Expected: {original_state}, Got: {state}")
        return None
    
    token_url = f"{AUTHORITY}/oauth2/v2.0/token"
    
    data = {
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'code': authorization_code,
        'grant_type': 'authorization_code',
        'redirect_uri': REDIRECT_URI,
        'scope': ' '.join(SCOPES)
    }
    
    try:
        response = requests.post(token_url, data=data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"Error exchanging code for token: {e}")
        return None



def invoke_bedrock_agent(prompt, access_token):
    """Invoke Bedrock AgentCore with Bearer token authentication"""
    
    # URL encode the agent ARN
    escaped_agent_arn = urllib.parse.quote(AGENT_ARN, safe='')
    
    # Construct the URL
    url = f"https://bedrock-agentcore.{AWS_REGION}.amazonaws.com/runtimes/{escaped_agent_arn}/invocations?qualifier=DEFAULT"
    
    # Set up headers with Bearer token
    headers = {
        "Authorization": f"Bearer {access_token}",
        "X-Amzn-Trace-Id": f"streamlit-{int(time.time())}", 
        "Content-Type": "application/json",
        "X-Amzn-Bedrock-AgentCore-Runtime-Session-Id": f"dfmeoagmreaklgmrkleafremoigrmtesogmtrskhmtkrlshmt"
    }
    
    # Prepare request payload
    payload = json.dumps({"prompt": prompt})
    
    try:
        # Make streaming request
        with requests.post(
            url,
            headers=headers,
            data=payload,
            stream=True,
            timeout=30
        ) as response:
            
            if response.status_code == 200:
                # Process streaming response
                full_response = ""
                response_container = st.empty()
                
                for line in response.iter_lines():
                    if line:
                        decoded_line = line.decode("utf-8")
                        
                        # Handle different streaming formats
                        if decoded_line.startswith("data:"):
                            try:
                                event = decoded_line[len("data: "):]
                                if event.strip() == "[DONE]":
                                    break
                                    
                                if '"message":' in event and '"text":' in event:
                                    obj = json.loads(event)
                                    for c in obj.get("message", {}).get("content", []):
                                        if "text" in c:
                                            full_response += c["text"]
                                            response_container.markdown(full_response)
                                elif '"content":' in event or '"text":' in event:
                                    obj = json.loads(event)
                                    if 'content' in obj:
                                        full_response += obj['content']
                                        response_container.markdown(full_response)
                                    elif 'text' in obj:
                                        full_response += obj['text']
                                        response_container.markdown(full_response)
                            except json.JSONDecodeError:
                                if event.strip():
                                    full_response += event
                                    response_container.markdown(full_response)
                        else:
                            # Handle non-SSE streaming format
                            try:
                                if decoded_line.strip():
                                    obj = json.loads(decoded_line)
                                    if isinstance(obj, dict):
                                        if 'content' in obj:
                                            full_response += obj['content']
                                        elif 'text' in obj:
                                            full_response += obj['text']
                                        else:
                                            full_response += str(obj)
                                        response_container.markdown(full_response)
                                    else:
                                        full_response += str(obj)
                                        response_container.markdown(full_response)
                            except json.JSONDecodeError:
                                full_response += decoded_line
                                response_container.markdown(full_response)
                
                return full_response
                
            elif response.status_code >= 400:
                try:
                    error_data = response.json()
                    st.error(f"Agent Error ({response.status_code}): {json.dumps(error_data, indent=2)}")
                except:
                    st.error(f"Agent Error ({response.status_code}): {response.text}")
                return None
            else:
                st.error(f"Unexpected status code: {response.status_code}")
                return None
                
    except requests.exceptions.RequestException as e:
        st.error(f"Error invoking agent: {str(e)}")
        return None

def main():
    st.set_page_config(
        page_title="Microsoft Authentication Agentcore Agent with Streaming Support",
        page_icon="",
        layout="wide"
    )
    
    st.title("Microsoft Authentication Agentcore Agent with Streaming Support")
    st.markdown("---")
    
    # Check for authorization code in URL parameters
    query_params = st.query_params
    
    if 'code' in query_params:
        authorization_code = query_params['code']
        state = query_params.get('state', None)
        
        # Get the original state from session if available, otherwise skip validation
        original_state = st.session_state.get('oauth_state', state)  # Fallback to received state
        
        with st.spinner("Exchanging authorization code for token..."):
            token_data = exchange_code_for_token(authorization_code, state, original_state)
        
        if token_data:
            st.session_state.access_token = token_data.get('access_token')
            st.session_state.refresh_token = token_data.get('refresh_token')
            
            # Get user info
            
            
            # Clear URL parameters and oauth state
            if 'oauth_state' in st.session_state:
                del st.session_state.oauth_state
            st.query_params.clear()
            st.rerun()
    
    # Check if user is authenticated
    if 'access_token' not in st.session_state:
        # Not authenticated - show login
        col1, col2, col3 = st.columns([1, 2, 1])
        
        with col2:
            st.markdown("### Please Login with Microsoft")
            st.markdown("You need to authenticate with your Microsoft account to use the agent.")
            
            if st.button("Login with Microsoft", use_container_width=True):
                auth_url, state = get_auth_url()
                st.session_state.oauth_state = state  # Store state for validation
                st.markdown(f"[Click here to login]({auth_url})")
                st.info("Click the link above to authenticate with Microsoft.")
            
            # Alternative: Show a simpler flow without state validation
            st.markdown("---")
            st.markdown("**Having issues with login?** Try the simplified flow:")
            if st.button(" Skip State Validation", use_container_width=True):
                auth_url, _ = get_auth_url()
                # Don't store state - this will skip validation
                st.markdown(f"[Click here to login (simplified)]({auth_url})")
                st.info("This login flow skips state validation for compatibility.")
    else:
        # Authenticated - show chat interface
        col1, col2 = st.columns([3, 1])
        
        with col1:
            if 'user_info' in st.session_state:
                user_info = st.session_state.user_info
                st.success(f" Logged in as: {user_info.get('displayName', 'Unknown')} ({user_info.get('mail', user_info.get('userPrincipalName', 'No email'))})")
        
        with col2:
            if st.button(" Logout"):
                # Clear session state
                for key in list(st.session_state.keys()):
                    del st.session_state[key]
                st.rerun()
        
        st.markdown("---")
        
        # Chat interface
        st.markdown("###  Chat with Bedrock Agent")
        
        # Initialize chat history
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        # Display chat messages
        for message in st.session_state.messages:
            with st.chat_message(message["role"]):
                st.markdown(message["content"])
        
        # Chat input
        if prompt := st.chat_input("Ask the agent anything..."):
            # Add user message to chat history
            st.session_state.messages.append({"role": "user", "content": prompt})
            
            # Display user message
            with st.chat_message("user"):
                st.markdown(prompt)
            
            # Get agent response
            with st.chat_message("assistant"):
                with st.spinner("Agent is thinking..."):
                    response = invoke_bedrock_agent(prompt, st.session_state.access_token)
                
                if response:
                    st.session_state.messages.append({"role": "assistant", "content": response})
        
        # Sidebar with additional info
        with st.sidebar:
            st.markdown("###  Configuration")
            st.markdown(f"**Agent ARN:** `{AGENT_ARN}`")
            
            
            if st.button(" Clear Chat History"):
                st.session_state.messages = []
                st.rerun()
            
            st.markdown("---")
            st.markdown("###  Session Info")
           

if __name__ == "__main__":
    main()