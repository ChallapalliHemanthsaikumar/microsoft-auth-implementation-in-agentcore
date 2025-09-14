from bedrock_agentcore.runtime import BedrockAgentCoreApp
from strands import Agent
from tools import add, subtract, multiply, get_nearby_places

app = BedrockAgentCoreApp()
agent = Agent(
    model="anthropic.claude-3-5-sonnet-20240620-v1:0",  # Specify the model you want to use
    tools=[add, subtract, multiply, get_nearby_places],
)

@app.entrypoint
async def agent_invocation(payload):
    """Handler for agent invocation"""
    user_message = payload.get(
        "prompt", "No prompt found in input, please guide customer to create a json payload with prompt key"
    )
    # return agent(user_message)


    stream = agent.stream_async(user_message)
    async for event in stream:
        print(event)
        yield (event)

if __name__ == "__main__":
    app.run()
