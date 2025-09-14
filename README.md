# Microsoft Authentication with AWS Bedrock AgentCore

This project demonstrates how to implement Microsoft OAuth authentication with AWS Bedrock AgentCore and create a streaming response agent with custom tools.

## 🎯 Overview

- **Microsoft OAuth Authentication**: Secure login using Microsoft Azure AD
- **Streaming Responses**: Real-time agent responses for better user experience
- **Custom Tools**: Built-in tools for calculations and location-based services
- **Streamlit UI**: User-friendly web interface for agent interaction

## 📋 Prerequisites

### Microsoft Azure Setup

1. **Create Azure App Registration**:
   - Go to [Azure Portal](https://portal.azure.com)
   - Navigate to "App registrations"
   - Create a new registration or use existing one

2. **Configure Authentication**:
   - Set Redirect URI: `http://localhost:8501`
   - Enable "Access tokens" and "ID tokens"
   - Set supported account types as needed

3. **Create Client Secret**:
   - Go to "Certificates & secrets"
   - Create a new client secret
   - Save the secret value (you'll need it later)

4. **API Permissions**:
   - Add the following permissions:
     - `email`
     - `offline_access`
     - `openid`
     - `profile`

5. **Create Custom Scope** (IMPORTANT):
   - Go to "Expose an API"
   - Create a scope named `access_as_user` (or any name you prefer)
   - This is mandatory for V2 tokens
   - Set admin and user consent

6. **Force V2 Tokens**:
   - In your app manifest, set `accessTokenAcceptedVersion` to `2`
   - This ensures your agent receives V2 tokens only

### AWS Setup

1. **Configure AWS Credentials**:
   ```bash
   aws configure
   ```

2. **Bedrock AgentCore Access**:
   - Ensure you have appropriate IAM permissions for Bedrock AgentCore
   - Region: `us-west-2` (or your preferred region)

## 🚀 Installation

1. **Clone the Repository**:
   ```bash
   git clone <repository-url>
   cd agentcore
   ```

2. **Create Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Configure Environment Variables**:
   Create a `.env` file with the following:
   ```env
   CLIENT_ID=your_azure_client_id
   CLIENT_SECRET=your_azure_client_secret
   TENANT_ID=your_tenant_id_or_common
   AUTHORITY=https://login.microsoftonline.com/common
   SCOPE=api://your_client_id/access_as_user
   ```

## 📁 Project Structure

```
agentcore/
├── agent.py                 # Main agent implementation with tools
├── streamlit.py            # Streamlit UI with Microsoft auth
├── invoke_deploy_agent.py  # Script to test deployed agent
├── container.py            # Container deployment script
├── tools.py               # Custom tools (calculations, places)
├── requirements.txt       # Python dependencies
├── .env                   # Environment variables
└── README.md             # This file
```

## 🔧 Configuration Files

### Required Dependencies (`requirements.txt`)
```
streamlit
requests
python-dotenv
msal
boto3
pyyaml
strands-agents-tools
strands-agents-builder
strands-agents
bedrock-agentcore
bedrock_agentcore_starter_toolkit
```

### Environment Variables (`.env`)
- `CLIENT_ID`: Your Azure app registration client ID
- `CLIENT_SECRET`: Your Azure app client secret
- `TENANT_ID`: Your Azure tenant ID (or "common")
- `AUTHORITY`: Microsoft authority URL
- `SCOPE`: Your custom API scope

## 🏃‍♂️ Running the Application

### 1. Local Agent Testing (No Authentication)
```bash
python agent.py
```
In another terminal:
```bash
python local_testing.py
```

### 2. Deploy Agent to AWS Bedrock AgentCore
```bash
python container.py
```

### 3. Run Streamlit UI with Microsoft Authentication
```bash
streamlit run streamlit.py
```

### 4. Test Deployed Agent with Access Token
```bash
python invoke_deploy_agent.py
```

## 🛠️ Features

### Custom Tools Available
- **Addition**: Add two numbers
- **Subtraction**: Subtract two numbers
- **Multiplication**: Multiply two numbers
- **Get Nearby Places**: Find famous places near a location

### Example Prompts
- "What is 5 + 3?"
- "Give me famous places near Seattle"
- "Calculate 10 * 7"
- "What are popular attractions in New York?"

## 🔐 Authentication Flow

1. **User Login**: Click "Login with Microsoft" in Streamlit
2. **OAuth Redirect**: User is redirected to Microsoft login
3. **Token Exchange**: Authorization code is exchanged for access token
4. **Agent Access**: Access token is used to authenticate with AgentCore
5. **Streaming Response**: Agent provides real-time streaming responses

## 📝 Important Notes

### Token Version Requirements
- **MUST use V2 tokens**: Set `accessTokenAcceptedVersion: 2` in Azure manifest
- **Custom scope required**: Create custom scope in Azure app registration
- **Bearer token authentication**: Agent expects OAuth tokens, not AWS SigV4

### Agent Configuration
- **OAuth Provider**: Configure in Bedrock AgentCore console
- **Allowed Audience**: Must match your Azure client ID
- **Discovery URL**: Use tenant-specific endpoint for better security

### Troubleshooting Common Issues

1. **"Authorization method mismatch"**:
   - Ensure agent is configured for OAuth, not SigV4
   - Use Bearer token in requests

2. **"Claim 'client_id' value mismatch"**:
   - Verify client ID matches between Azure and AgentCore
   - Check token audience claim

3. **"app_id is null"**:
   - Ensure custom scope is properly configured
   - Verify V2 token configuration

## 🔗 API Endpoints

### Agent Invocation
```
POST https://bedrock-agentcore.{region}.amazonaws.com/runtimes/{agent_arn}/invocations?qualifier=DEFAULT
```

### Headers Required
```
Authorization: Bearer {access_token}
Content-Type: application/json
X-Amzn-Bedrock-AgentCore-Runtime-Session-Id: {session_id}
```

## 🧪 Testing

### Local Testing
Test your agent locally without authentication:
```bash
python agent.py
```

### Production Testing
Test deployed agent with Microsoft authentication:
1. Run Streamlit app
2. Login with Microsoft
3. Use the chat interface
4. Or copy access token for manual testing

## 📊 Monitoring

- **Agent Logs**: Available in CloudWatch
- **Streaming**: Real-time response updates in UI
- **Error Handling**: Comprehensive error messages and debugging

## 🤝 Contributing

1. Fork the repository
2. Create your feature branch
3. Commit your changes
4. Push to the branch
5. Create a Pull Request

## 📄 License

This project is licensed under the MIT License - see the LICENSE file for details.

## 🆘 Support

If you encounter issues:
1. Check the troubleshooting section above
2. Verify your Azure app registration configuration
3. Ensure AWS credentials are properly configured
4. Check CloudWatch logs for detailed error messages

## 🎥 Demo

Watch the complete video tutorial: **[Microsoft Authentication in AWS Bedrock AgentCore + Streaming AI Agent](https://youtu.be/LEiOtsYEpWk)**

The project includes a complete working example with:
- Microsoft authentication flow
- Real-time streaming responses
- Custom tool integration
- Professional UI with Streamlit

---

**Happy coding! 🚀**
