
from dotenv import load_dotenv
import os
from bedrock_agentcore_starter_toolkit import Runtime
import os





load_dotenv()
TENANT_ID = os.environ.get("TENANT_ID")



CLIENT_ID = os.environ.get("CLIENT_ID")


agentcore_runtime = Runtime()
discovery_url = f"https://login.microsoftonline.com/{TENANT_ID}/v2.0/.well-known/openid-configuration"

response = agentcore_runtime.configure(
    entrypoint="agent.py",
    auto_create_execution_role=True,
    auto_create_ecr=True,
    requirements_file="requirements.txt",
    region=os.environ.get("REGION", "us-west-2"),
    agent_name="strands_wo_memory_entra_inbound",
    authorizer_configuration={
        "customJWTAuthorizer": {
            "discoveryUrl": discovery_url,
            "allowedAudience": [CLIENT_ID]
        }
    }
)
print(response)
launch_result = agentcore_runtime.launch()
print(launch_result)