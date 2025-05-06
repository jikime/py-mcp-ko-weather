# Korea Weather MCP Server

[![smithery badge](https://smithery.ai/badge/@jikime/py-mcp-ko-weather)](https://smithery.ai/server/@jikime/py-mcp-ko-weather) ![](https://badge.mcpx.dev?type=server 'MCP Server') ![Version](https://img.shields.io/badge/version-1.1.10-green) ![License](https://img.shields.io/badge/license-MIT-blue)

This MCP (Multi-platform Communication Protocol) server provides access to Korea Meteorological Administration (KMA) APIs, allowing AI agents to retrieve weather forecast information for locations in South Korea.

## Overview

- Retrieve precise grid coordinates for Korean administrative regions
- Get detailed short-term weather forecasts for any location in Korea
- Support for all Korean administrative divisions (city, district, neighborhood)
- Structured text responses optimized for LLM consumption
- Comprehensive weather data including temperature, precipitation, sky condition, humidity, wind direction, and wind speed

## Table of Contents

- [Prerequisites](#prerequisites)
- [Installation](#installation)
- [Configure MCP Settings](#configure-mcp-settings)
- [API Reference](#api-reference)
- [Acknowledgements](#acknowledgements)
- [License](#license)

## Setup

### Prerequisites

- Python 3.12+
- Korea Meteorological Administration API credentials
- You can obtain the API credentials by signing up at the [Public Data Portal](https://www.data.go.kr/) and requesting access to the "기상청_단기예보 ((구)_동네예보) 조회서비스" API.

### Installation

1. Clone the repository:
```bash
git clone https://github.com/jikime/py-mcp-ko-weather.git
cd py-mcp-ko-weather
```

2. uv installation
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. Create a virtual environment and install dependencies:
```bash
uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

4. Create a `.env` file with your KMA API credentials:
```
cp env.example .env
vi .env

KO_WEATHER_API_KEY=your_api_key_here
```

5. Migrate the grid coordinates data from Excel to SQLite:
```bash
uv run src/migrate.py
```

#### Using Docker

1. Build the Docker image:
```bash
docker build -t py-mcp-ko-weather .
```

2. Run the container:
```bash
docker run py-mcp-ko-weather
```

#### Using Local

1. Run the server:
```bash
mcp run src/server.py
```
2. Run the MCP Inspector
```bash
mcp dev server.py
```

## Configure MCP Settings
Add the server configuration to your MCP settings file:

#### Claude desktop app 
1. To install automatically via [Smithery](https://smithery.ai/server/@jikime/py-mcp-ko-weather):

```bash
npx -y @smithery/cli install @jikime/py-mcp-ko-weather --client claude
```

2. To install manually
open `~/Library/Application Support/Claude/claude_desktop_config.json`

Add this to the `mcpServers` object:
```json
{
  "mcpServers": {
    "Google Toolbox": {
      "command": "/path/to/bin/uv",
      "args": [
        "--directory",
        "/path/to/py-mcp-ko-weather",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

#### Cursor IDE 
open `~/.cursor/mcp.json`

Add this to the `mcpServers` object:
```json
{
  "mcpServers": {
    "Google Toolbox": {
      "command": "/path/to/bin/uv",
      "args": [
        "--directory",
        "/path/to/py-mcp-ko-weather",
        "run",
        "src/server.py"
      ]
    }
  }
}
```

#### for Docker
```json
{
  "mcpServers": {
    "Google Toolbox": {
      "command": "docker",
      "args": [
        "run",
        "-i",
        "--rm",
        "py-mcp-ko-weather"
      ]
    }
  }
}
```

### Using with Claude

Once configured, you can ask Claude questions like:
- "서울특별시 서초구 양재1동의 날씨는?"
- "부산광역시 해운대구 우동의 날씨 예보를 알려줘"
- "경기도 성남시 분당구의 현재 기온은?"

## API Reference

### Tools

#### Get Grid Location
```
get_grid_location(city: str, gu: str, dong: str) -> dict
```
Retrieves the grid coordinates (nx, ny) used by the Korea Meteorological Administration API for the specified location. 
This tool searches the database for the exact coordinates based on city/province, district/county, and neighborhood/town information.

#### Get Forecast
```
get_forecast(city: str, gu: str, dong: str, nx: int, ny: int) -> str
```
Calls the KMA's ultra-short-term forecast API to provide weather forecast information for a specific location.
Returns comprehensive weather data including temperature, precipitation, sky condition, humidity, wind direction, and wind speed.

### Resources

#### Weather Instructions
```
GET weather://instructions
```
Provides detailed documentation on how to use the Korea Weather MCP server, including tool workflows and response formats.

### Prompts

#### Weather Query
The server includes a structured prompt template for guiding conversations about weather queries, ensuring efficient information gathering and clear presentation of forecast data.

## Response Format

Weather forecast responses are provided in structured text format, optimized for LLM processing:

```
Weather forecast for 서울특별시 서초구 양재1동 (coordinates: nx=61, ny=125)
Date: 2025-05-01
Time: 15:00

Current conditions:
Temperature: 22.3°C
Sky condition: Mostly clear
Precipitation type: None
Precipitation probability: 0%
Humidity: 45%
Wind direction: Northwest
Wind speed: 2.3 m/s

Hourly forecast:
16:00 - Temperature: 21.8°C, Sky: Clear, Precipitation: None
17:00 - Temperature: 20.5°C, Sky: Clear, Precipitation: None
18:00 - Temperature: 19.2°C, Sky: Clear, Precipitation: None
...
```

## Acknowledgements

- [Korea Meteorological Administration](https://www.kma.go.kr/)
- [Public Data Portal](https://www.data.go.kr/)
- [MCP Protocol](https://github.com/mcp-foundation/mcp-spec)

## License

This project is licensed under the MIT License - see the LICENSE file for details.
