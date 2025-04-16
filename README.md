# Python MCP Korea Weather Service

MCP (Model Control Protocol) 서버를 이용한 한국 기상 정보 제공 서비스입니다.

## 설치 방법

1. 이 저장소를 클론합니다:
```bash
git clone https://github.com/yourusername/py-mcp-ko-weather.git
cd py-mcp-ko-weather
```

2. 필요한 패키지를 설치합니다:
```bash
pip install -e .
```

3. .env 파일에 기상청 API 키를 설정합니다:
```
KO_WEATHER_API_KEY=your_api_key_here
```

## 기상청 API 키 발급 방법

1. [공공데이터포털](https://www.data.go.kr/)에 접속하여 회원가입 및 로그인합니다.
2. "초단기예보조회" API를 검색하여 활용신청합니다.
3. 승인 후 받은 API 키를 .env 파일에 설정합니다.

## 실행 방법

```bash
cd src
python server.py
```

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

1. **날씨 서비스 사용 설명서 (`weather-instructions`)**
   - URI: `weather-instructions`
   - 설명: 한국 기상 서비스의 사용 방법을 설명하는 상세 가이드입니다. 이 리소스는 도구 사용 방법, 워크플로우, 응답 형식 등 서비스 사용에 필요한 모든 정보를 제공합니다. LLM이 날씨 도구를 효과적으로 활용할 수 있도록 구조화된 정보를 포함합니다.

2. **날씨 카테고리 코드 설명 (`weather-categories`)**
   - URI: `weather-categories`
   - 설명: 기상청 API에서 제공하는 각 날씨 카테고리에 대한 상세 설명입니다. 이 리소스는 각 카테고리 코드의 의미, 단위, 해석 방법을 제공하여 LLM이 날씨 예보 데이터를 올바르게 이해하고 해석할 수 있도록 도와줍니다.

### 프롬프트 (Prompts)

1. **날씨 정보 조회 프롬프트 (`weather-query`)**
   - 설명: 한국 지역의 날씨 정보를 조회하기 위한 대화형 프롬프트 템플릿입니다. 이 프롬프트는 사용자와 LLM 간의 구조화된 대화를 안내하며, 적절한 도구 사용 순서와 응답 형식을 제시합니다. 사용자로부터 필요한 정보를 수집하고 날씨 예보를 명확하게 제공하는 방법을 담고 있습니다.

2. **위치 검색 프롬프트 (`location-search`)**
   - 설명: 사용자가 입력한 부분적인 위치 정보를 바탕으로 정확한 행정구역 정보를 유도하기 위한 프롬프트 템플릿입니다. 이 프롬프트는 사용자가 불완전한 위치 정보(예: 시/도 없이 구/동만 제공)를 입력했을 때 적절한 질문을 통해 완전한 정보를 수집하는 과정을 안내합니다.

## MCP 서버 사용 예시

### 클라이언트 코드 예시

```python
from mcp.client import Client

# MCP 클라이언트 생성
client = Client("http://localhost:8000")

# 위치 좌표 조회
location_info = client.get_grid_location(city="서울특별시", gu="서초구", dong="양재1동")
print(location_info)
# 출력: City(시): 서울특별시, Gu(구): 서초구, Dong(동): 양재1동, Nx: 61, Ny: 125

# 좌표 추출 (문자열 파싱)
nx = int(location_info.split("Nx: ")[1].split(",")[0])
ny = int(location_info.split("Ny: ")[1])

# 날씨 예보 조회
forecast = client.get_forecast(city="서울특별시", gu="서초구", dong="양재1동", nx=nx, ny=ny)
print(forecast)
```

### 리소스 사용 예시

```python
from mcp.client import Client

# MCP 클라이언트 생성
client = Client("http://localhost:8000")

# 날씨 서비스 사용 설명서 조회
instructions = client.resource("weather-instructions")
print(instructions)

# 날씨 카테고리 코드 설명 조회
categories = client.resource("weather-categories")
print(categories)
```

### 프롬프트 사용 예시 (MCP 서버와 LLM 연동 시)

```python
from mcp.client import Client
from mcp.llm import LLMProvider

# MCP 클라이언트 생성
client = Client("http://localhost:8000")

# LLM 프로바이더 설정 (예시)
llm = LLMProvider("your_llm_provider")

# 날씨 정보 조회 프롬프트 사용
prompt = client.prompt("weather-query")
user_query = "서울 서초구 양재동 날씨 어때요?"

# LLM에 프롬프트와 사용자 쿼리 전송
response = llm.generate(prompt=prompt, user_input=user_query, tools=[client.get_tool("get_grid_location"), client.get_tool("get_forecast")])
print(response)
```

## 라이센스

MIT
