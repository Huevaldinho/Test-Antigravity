import os
import asyncio
import sys
from mcp import ClientSession, StdioServerParameters
from mcp.client.stdio import stdio_client
from google import genai
from google.genai import types

# Configuration
# We will run the server by executing the Docker container command.
# This assumes 'docker-compose up' is running or the image is built.
# Actually, to use stdio with a running container, we use 'docker exec'.
# Or we can just run the docker run command directly as the server process.

SERVER_DOCKER_CONTAINER = "bq-mcp-server"

async def main():
    print("🤖 Starting Gemini MCP Client...")
    
    api_key = os.getenv("GOOGLE_API_KEY")
    if not api_key:
        print("❌ GOOGLE_API_KEY environment variable not found.")
        return

    # Initialize Gemini Client
    client = genai.Client(api_key=api_key)

    # Define the server parameters
    # We tell the MCP client to run "docker exec -i bq-mcp-server python server.py"
    # This connects our local python script to the stdin/stdout of the server inside Docker.
    server_params = StdioServerParameters(
        command="docker",
        args=["exec", "-i", SERVER_DOCKER_CONTAINER, "python", "server.py"],
        env=None
    )

    print(f"🔌 Connecting to MCP Server in Docker container: {SERVER_DOCKER_CONTAINER}...")

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            # 1. Initialize
            await session.initialize()
            
            # 2. List Tools
            tools = await session.list_tools()
            print(f"🛠️  Connected! Found {len(tools.tools)} tools:")
            for tool in tools.tools:
                print(f"   - {tool.name}: {tool.description}")

            # 3. Chat Loop
            print("\n💬 Chat session started. Type 'exit' to quit.")
            print("--------------------------------------------------")
            
            chat = client.chats.create(model="gemini-1.5-flash")
            
            # We need to inform Gemini about the tools.
            # In a real app, we would convert MCP tool definitions to Gemini tool definitions.
            # For this simple POC, we'll just instruct the model in the prompt or use the raw tool definitions if compatible.
            # The google-genai SDK supports tool calling. We need to map them.
            
            # Mapping MCP tools to Gemini Tools
            gemini_tools = []
            for t in tools.tools:
                # Simplified mapping
                gemini_tools.append({
                    "name": t.name,
                    "description": t.description,
                    "parameters": t.inputSchema
                })
            
            # Configure the chat with tools
            # Note: The SDK syntax might vary slightly, this is a generic implementation.
            
            while True:
                user_input = input("\nYou: ")
                if user_input.lower() in ["exit", "quit"]:
                    break

                # Send message to Gemini
                # We need to handle the tool calling loop manually here or use automatic function calling if supported.
                # For this exercise, let's do a simple manual loop:
                # 1. Send prompt
                # 2. If model wants to call tool -> Execute tool -> Send result back
                
                # Construct the system instruction to use tools
                prompt = f"""
                You are a helpful assistant with access to a BigQuery database via tools.
                User Query: {user_input}
                
                Available Tools:
                {gemini_tools}
                
                If you need to use a tool, respond ONLY with a JSON object:
                {{"tool": "tool_name", "arguments": {{...}}}}
                
                If you have the answer, just reply normally.
                """
                
                response = chat.send_message(prompt)
                response_text = response.text
                
                # Check if it looks like a tool call (Basic JSON check)
                if response_text.strip().startswith('{"tool"'):
                    import json
                    try:
                        tool_call = json.loads(response_text)
                        tool_name = tool_call["tool"]
                        tool_args = tool_call["arguments"]
                        
                        print(f"⚙️  Model requested tool: {tool_name}")
                        
                        # Execute Tool via MCP
                        result = await session.call_tool(tool_name, arguments=tool_args)
                        
                        # Send result back to model
                        tool_output = result.content[0].text
                        print(f"   > Result: {tool_output[:100]}...") # Truncate log
                        
                        final_response = chat.send_message(f"Tool Output: {tool_output}\n\nNow answer the user's question.")
                        print(f"🤖 Gemini: {final_response.text}")
                        
                    except Exception as e:
                        print(f"❌ Error executing tool: {e}")
                        print(f"🤖 Gemini (Raw): {response_text}")
                else:
                    print(f"🤖 Gemini: {response_text}")

if __name__ == "__main__":
    # Check if docker is running
    # This is just a client script.
    asyncio.run(main())
