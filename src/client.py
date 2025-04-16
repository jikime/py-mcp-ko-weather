from mcp import ClientSession, StdioServerParameters, types
from mcp.client.stdio import stdio_client


# Create server parameters for stdio connection
server_params = StdioServerParameters(
    command=".venv/bin/python",  # Executable
    args=["src/server.py"],  # Path to the server script
    env=None,  # Optional environment variables
)

async def run():
    async with stdio_client(server_params) as (read, write):
        async with ClientSession(
            read, write
        ) as session:
            # Initialize the connection
            await session.initialize()

            # List available prompts
            prompts = await session.list_prompts()
            print(f"Available prompts: {prompts}")

            # Get the weather query prompt
            weather_prompt = await session.get_prompt("weather-query")
            print(f"Weather prompt: {weather_prompt}")

            # List available resources
            resources = await session.list_resources()
            print(f"Available resources: {resources}")

            # Get weather instructions resource
            instructions, mime_type = await session.read_resource("weather://instructions")
            print(f"Weather instructions: {instructions}")

            # List available tools
            tools = await session.list_tools()
            print(f"Available tools: {tools}")

            # Example: Call get_grid_location tool
            location = "서울특별시"
            gu = "서초구"
            dong = "양재1동"
            grid_result = await session.call_tool(
                "get_grid_location", 
                arguments={
                    "city": location,
                    "gu": gu,
                    "dong": dong
                }
            )
            print(f"Grid location result: {grid_result}")
            
            print(grid_result.content[0].text)

            # Parse the grid result to get nx and ny values
            # This is a simple example parser - adjust based on the actual response format
            nx, ny = 61, 125  # Default values
            try:
                # content는 TextContent 객체의 리스트입니다
                if grid_result.content and len(grid_result.content) > 0:
                    # 첫 번째 텍스트 콘텐츠를 가져옵니다
                    result_text = grid_result.content[0].text
                    if not result_text.startswith("No location") and not result_text.startswith("Error"):
                        result_parts = result_text.split(", ")
                        for part in result_parts:
                            if part.startswith("Nx:"):
                                nx = int(part.split(" ")[1])
                            elif part.startswith("Ny:"):
                                ny = int(part.split(" ")[1])
            except Exception as e:
                print(f"Error parsing grid result: {e}")

            # Example: Call get_forecast tool
            forecast_result = await session.call_tool(
                "get_forecast",
                arguments={
                    "city": location,
                    "gu": gu,
                    "dong": dong,
                    "nx": nx,
                    "ny": ny
                }
            )
            print(f"Forecast result: {forecast_result}")


if __name__ == "__main__":
    import asyncio

    asyncio.run(run())
