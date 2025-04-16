# Python MCP Korea Weather Service
[![smithery badge](https://smithery.ai/badge/@jikime/py-mcp-ko-weather)](https://smithery.ai/server/@jikime/py-mcp-ko-weather)

MCP (Model Control Protocol) 서버를 이용한 한국 기상 정보 제공 서비스입니다.

## 설치 방법
### Installing via Smithery

To install Korea Weather Service for Claude Desktop automatically via [Smithery](https://smithery.ai/server/@jikime/py-mcp-ko-weather):

```bash
npx -y @smithery/cli install @jikime/py-mcp-ko-weather --client claude
```

### Manual Installation

1. 이 저장소를 클론합니다:
```bash
git clone https://github.com/jikime/py-mcp-ko-weather.git
cd py-mcp-ko-weather
```

2. uv 설치
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

3. uv를 사용하여 가상환경을 생성하고 필요한 패키지를 설치합니다:
```bash
uv venv -p 3.12
source .venv/bin/activate
uv pip install -r requirements.txt
```

4. .env 파일에 기상청 API 키를 설정합니다:
```
cp env.example .env
vi .env
KO_WEATHER_API_KEY=your_api_key_here
```

5. 엑셀의 기상청 격자 좌표의 데이타를 SQLite로 마이그레이션합니다.
```bash
uv run src/migrate.py
```

## 기상청 API 키 발급 방법

1. [공공데이터포털](https://www.data.go.kr/)에 접속하여 회원가입 및 로그인합니다.
2. "기상청_단기예보 ((구)_동네예보) 조회서비스" API를 검색하여 활용신청합니다.
3. 승인 후 받은 API 키를 .env 파일에 설정합니다.

## MCP 도구 구성하기

~/Library/Application\ Support/Claude/claude_desktop_config.json 파일을 열고 날씨 서버를 추가합니다.
```json
{
    "mcpServers": {
      "Korea Weather": {
        "command": "/Users/jikime/Dev/.local/bin/uv",
        "args": [
          "--directory",
          "/Users/jikime/Dev/py-mcp-ko-weather",
          "run",
          "src/server.py"
        ]
      }
    }
}
```

## 실행 방법

- Claude Desktop 을 실행하여 도구에 추가되었는지 확인합니다.
- 채팅 입력창에 "서울특별시 서초구 양재1동"의 날씨는?" 라고 입력해보세요.


## 기능 설명

이 MCP 서버는 다음과 같은 기능들을 제공합니다:

### 도구 (Tools)

1. **위치 좌표 조회 (`get_grid_location`)**
   - 설명: 한국 기상청 API에 사용되는 격자 좌표(nx, ny)를 조회합니다. 사용자가 입력한 시/도, 구/군, 동/읍/면 정보를 바탕으로 해당 지역의 기상청 격자 좌표를 데이터베이스에서 검색하여 반환합니다. 이 도구는 기상청 API 호출에 필요한 정확한 좌표값을 얻기 위해 필수적으로 사용됩니다.
   - 파라미터:
     - `city`: 시/도 이름 (예: "서울특별시")
     - `gu`: 구/군 이름 (예: "서초구")
     - `dong`: 동/읍/면 이름 (예: "양재1동")
   - 데이터는 내장된 SQLite 데이터베이스(`data/weather_grid.db`)에서 조회됩니다.

2. **날씨 예보 조회 (`get_forecast`)**
   - 설명: 한국 기상청의 초단기예보 API를 호출하여 특정 지역의 날씨 예보 정보를 제공합니다. 사용자가 입력한 지역 정보와 격자 좌표를 바탕으로 현재 시점에서의 기상 정보를 조회합니다. 이 도구는 온도, 강수량, 하늘상태, 습도, 풍향, 풍속 등 상세한 기상 정보를 포함하며, 6시간 이내의 단기 예보를 제공합니다.
   - 파라미터:
     - `city`: 시/도 이름 (예: "서울특별시")
     - `gu`: 구/군 이름 (예: "서초구")
     - `dong`: 동/읍/면 이름 (예: "양재1동")
     - `nx`: X 격자 좌표
     - `ny`: Y 격자 좌표

### 리소스 (Resources)

**날씨 서비스 사용 설명서 (`weather-instructions`)**
   - URI: `weather-instructions`
   - 설명: 한국 기상 서비스의 사용 방법을 설명하는 상세 가이드입니다. 이 리소스는 도구 사용 방법, 워크플로우, 응답 형식 등 서비스 사용에 필요한 모든 정보를 제공합니다. LLM이 날씨 도구를 효과적으로 활용할 수 있도록 구조화된 정보를 포함합니다.

### 프롬프트 (Prompts)

**날씨 정보 조회 프롬프트 (`weather-query`)**
   - 설명: 한국 지역의 날씨 정보를 조회하기 위한 대화형 프롬프트 템플릿입니다. 이 프롬프트는 사용자와 LLM 간의 구조화된 대화를 안내하며, 적절한 도구 사용 순서와 응답 형식을 제시합니다. 사용자로부터 필요한 정보를 수집하고 날씨 예보를 명확하게 제공하는 방법을 담고 있습니다.

## 라이센스

Apache License 2.0
