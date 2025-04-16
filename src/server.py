import sqlite3
from pathlib import Path
from dotenv import load_dotenv
from mcp.server.fastmcp import FastMCP
from api import get_forecast_api

# Create an MCP server
mcp = FastMCP("Korea Weather Service")

@mcp.tool(
    name="get_grid_location",
    description="한국 기상청 API에 사용되는 격자 좌표(nx, ny)를 조회합니다. 사용자가 입력한 시/도, 구/군, 동/읍/면 정보를 바탕으로 해당 지역의 기상청 격자 좌표를 데이터베이스에서 검색하여 반환합니다. 이 도구는 기상청 API 호출에 필요한 정확한 좌표값을 얻기 위해 필수적으로 사용됩니다."
)
def get_grid_location(city: str, gu: str, dong: str) -> str:
    """Get grid location(nx, ny) for Korea Weather
    
    Args:
        city: City Name (e.g. 서울특별시)
        gu: Gu Name (e.g. 서초구)
        dong: Dong Name (e.g. 양재1동)
    """
    try:
        # Connect to SQLite database
        db_path = Path(__file__).parent.parent / "data" / "weather_grid.db"
        
        if not db_path.exists():
            return f"Error: Database not found at {db_path}"
        
        conn = sqlite3.connect(db_path)
        cursor = conn.cursor()

        # Query the database for the grid coordinates
        query = """
        SELECT level1, level2, level3, grid_x, grid_y 
        FROM weather_grid 
        WHERE level1 LIKE ? AND level2 LIKE ? AND level3 LIKE ?
        """
        cursor.execute(query, (f"%{city}%", f"%{gu}%", f"%{dong}%"))
        result = cursor.fetchone()
        
        if not result:
            return f"No location found for City: {city}, Gu: {gu}, Dong: {dong}"
        
        level1, level2, level3, nx, ny = result
        
        # Close the connection
        conn.close()
        
        # Return formatted string
        return f"City(시): {level1}, Gu(구): {level2}, Dong(동): {level3}, Nx: {nx}, Ny: {ny}"
    
    except Exception as e:
        return f"Error retrieving grid location: {str(e)}"


@mcp.tool(
    name="get_forecast",
    description="한국 기상청의 초단기예보 API를 호출하여 특정 지역의 날씨 예보 정보를 제공합니다. 사용자가 입력한 지역 정보와 격자 좌표를 바탕으로 현재 시점에서의 기상 정보를 조회합니다. 이 도구는 온도, 강수량, 하늘상태, 습도, 풍향, 풍속 등 상세한 기상 정보를 포함하며, 6시간 이내의 단기 예보를 제공합니다."
)
async def get_forecast(city: str, gu: str, dong: str, nx: int, ny: int) -> str:
    """Get weather forecast for a location.
    
    Args:
        city: City Name (e.g. 서울특별시)
        gu: Gu Name (e.g. 서초구)
        dong: Dong Name (e.g. 양재1동)
        nx: Grid X coordinate
        ny: Grid Y coordinate
    """
    return await get_forecast_api(city, gu, dong, nx, ny)


@mcp.resource(
    uri="weather://instructions",
    name="Korea Weather Service Instructions", 
    description="한국 기상 서비스의 사용 방법을 설명하는 상세 가이드입니다. 이 리소스는 도구 사용 방법, 워크플로우, 응답 형식 등 서비스 사용에 필요한 모든 정보를 제공합니다. LLM이 날씨 도구를 효과적으로 활용할 수 있도록 구조화된 정보를 포함합니다."
)
def get_weather_instructions() -> str:
    """Resource that provides detailed instructions on how to use the weather service tools."""
    return """
    # Korea Weather Service Instructions
    
    This service provides tools to get weather information for locations in Korea.
    
    ## Available Tools
    
    1. `get_grid_location(city, gu, dong)` - Get grid coordinates (nx, ny) for a location
       - Example: get_grid_location(city="서울특별시", gu="서초구", dong="양재1동")
    
    2. `get_forecast(city, gu, dong, nx, ny)` - Get weather forecast for a location
       - Example: get_forecast(city="서울특별시", gu="서초구", dong="양재1동", nx=61, ny=125)
    
    ## Workflow
    
    1. First, use `get_grid_location` to obtain the grid coordinates (nx, ny) for your location
    2. Then, use those coordinates with `get_forecast` to get the weather forecast
    
    ## Response Format
    
    The forecast includes information such as:
    - Temperature (°C)
    - Precipitation (mm)
    - Sky condition (clear, cloudy, etc.)
    - Humidity (%)
    - Wind speed and direction
    """

@mcp.prompt(
    name="weather-query",
    description="한국 지역의 날씨 정보를 조회하기 위한 대화형 프롬프트 템플릿입니다. 이 프롬프트는 사용자와 LLM 간의 구조화된 대화를 안내하며, 적절한 도구 사용 순서와 응답 형식을 제시합니다. 사용자로부터 필요한 정보를 수집하고 날씨 예보를 명확하게 제공하는 방법을 담고 있습니다."
)
def weather_query_prompt() -> str:
    """A prompt template for querying weather information for Korean locations."""
    return """
    # Korea Weather Query
    
    You are a helpful weather information assistant for Korea. 
    Use the tools available to provide accurate weather information.
    
    ## Instructions
    
    1. Help the user find the weather forecast for their location in Korea.
    2. First use the `get_grid_location` tool to find the grid coordinates (nx, ny) for the specified location.
    3. Then use the `get_forecast` tool with those coordinates to get the detailed weather forecast.
    4. Present the weather information in a clear, organized format.
    5. If the user doesn't specify a complete location (city, gu, and dong), ask for clarification.
    
    ## Example Interaction
    
    User: What's the weather like in 서초구 양재동?
    
    Assistant: I need to know the city as well. Could you please provide the complete location (city, gu, dong)?
    
    User: 서울특별시 서초구 양재1동
    
    Assistant: Let me check the weather for 서울특별시 서초구 양재1동.
    [Uses get_grid_location to get coordinates]
    [Uses get_forecast with those coordinates]
    Here's the current weather and forecast for 서울특별시 서초구 양재1동...
    
    ## Response Format
    
    When providing weather information, include:
    1. Current conditions (temperature, precipitation, sky condition)
    2. Short-term forecast (next few hours)
    3. Any relevant weather warnings or advisories
    """

if __name__ == "__main__":
    # Run the MCP server
    mcp.run(transport='stdio')
