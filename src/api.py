import os 
from datetime import datetime, timedelta
import asyncio
from dotenv import load_dotenv
from utils import make_api_request

load_dotenv()

USER_AGENT = "weather-app/1.0"
wind_direction_kr = {
  'N': '북',
  'NNE': '북북동',
  'NE': '북동',
  'ENE': '동북동',
  'E': '동',
  'ESE': '동남동',
  'SE': '남동',
  'SSE': '남남동',
  'S': '남',
  'SSW': '남남서',
  'SW': '남서',
  'WSW': '서남서',
  'W': '서',
  'WNW': '서북서',
  'NW': '북서',
  'NNW': '북북서'
};
deg_code = {0 : 'N', 360 : 'N', 180 : 'S', 270 : 'W', 90 : 'E', 22.5 :'NNE',
           45 : 'NE', 67.5 : 'ENE', 112.5 : 'ESE', 135 : 'SE', 157.5 : 'SSE',
           202.5 : 'SSW', 225 : 'SW', 247.5 : 'WSW', 292.5 : 'WNW', 315 : 'NW',
           337.5 : 'NNW'}
pyt_code = {0 : '강수 없음', 1 : '비', 2 : '비/눈', 3 : '눈', 5 : '빗방울', 6 : '진눈깨비', 7 : '눈날림'}
sky_code = {1 : '맑음', 3 : '구름많음', 4 : '흐림'}

def format_weather_features(features: dict) -> str:
  formatted_features = []
  for key, value in features.items():
    if key == 'sky':
      formatted_features.append(f"하늘 상태: {value}")
    elif key == 'rain':
      formatted_features.append(f"강수 형태: {value}")
    elif key == 'rain_amount':
      formatted_features.append(f"강수량: {value}mm")
    elif key == 'temp':
      formatted_features.append(f"기온: {value}℃")
    elif key == 'humidity':
      formatted_features.append(f"습도: {value}%")
    elif key == 'wind_direction':
      formatted_features.append(f"풍향: {value}")
    elif key == 'wind_speed':
      formatted_features.append(f"풍속: {value}m/s")
  return "\n".join(formatted_features)
          
def deg_to_dir(deg) :
    close_dir = ''
    min_abs = 360
    if deg not in deg_code.keys() :
        for key in deg_code.keys() :
            if abs(key - deg) < min_abs :
                min_abs = abs(key - deg)
                close_dir = deg_code[key]
    else : 
        close_dir = deg_code[deg]
    return wind_direction_kr[close_dir]


async def get_forecast_api(city: str, gu: str, dong: str, nx: float, ny: float) -> str:
  try:
    serviceKey = os.environ.get("KO_WEATHER_API_KEY")
    if not serviceKey:
      raise ValueError("KO_WEATHER_API_KEY 환경변수가 설정되지 않았습니다.")
    
    
    base_date = datetime.now().strftime("%Y%m%d") # 발표 일자
    base_time = datetime.now().strftime("%H%M") # 발표 시간
    # nx = '62' # 예보 지점 x좌표
    # ny = '123' # 예보 지점 y좌표
    
    # 알고 싶은 시간
    input_d = datetime.strptime(base_date + base_time, "%Y%m%d%H%M" )
    
    # 실제 입력 시간
    input_d = datetime.strptime(base_date + base_time, "%Y%m%d%H%M" ) - timedelta(hours=1)
    
    input_datetime = datetime.strftime(input_d, "%Y%m%d%H%M")
    input_date = input_datetime[:-4]
    input_time = input_datetime[-4:]
    
    # url
    url = f"http://apis.data.go.kr/1360000/VilageFcstInfoService_2.0/getUltraSrtFcst?serviceKey={serviceKey}&numOfRows=60&pageNo=1&dataType=json&base_date={input_date}&base_time={input_time}&nx={nx}&ny={ny}"
    
    data = await make_api_request(url)
    
    if not data:
      raise ValueError("API 요청 결과가 비어있습니다.")
    
    if 'response' not in data:
      raise KeyError("API 응답에 'response' 항목이 없습니다.")
    
    if 'body' not in data['response']:
      raise KeyError("API 응답에 'body' 항목이 없습니다.")
    
    if 'items' not in data['response']['body']:
      raise KeyError("API 응답에 'items' 항목이 없습니다.")
    
    if 'item' not in data['response']['body']['items']:
      raise KeyError("API 응답에 'item' 항목이 없습니다.")
    
    res = data['response']['body']['items']['item']
    if not res:
      return [f"{city} {gu} {dong} 지역의 날씨 정보를 찾을 수 없습니다."]

    informations = dict()
    for items in res:
      try:
        cate = items['category']
        fcstTime = items['fcstTime']
        fcstValue = items['fcstValue']
        
        if fcstTime not in informations.keys():
          informations[fcstTime] = dict()
        
        informations[fcstTime][cate] = fcstValue
      except KeyError as e:
        print(f"날씨 데이터 항목 누락: {e}")
        continue

    if not informations:
      return [f"{city} {gu} {dong} 지역의 날씨 정보를 처리할 수 없습니다."]

    forecasts = []
    for key, val in zip(informations.keys(), informations.values()):
      features = dict()
      try:
        template = f"""{base_date[:4]}년 {base_date[4:6]}월 {base_date[-2:]}일 {key[:2]}시 {key[2:]}분 {city} {gu} {dong} 지역의 날씨는 """
        
        # 하늘 상태
        if 'SKY' in val and val['SKY']:
          try:
            sky_temp = sky_code[int(val['SKY'])]
            features['sky'] = sky_temp
          except (ValueError, KeyError):
            print(f"하늘 상태 코드 처리 오류: {val['SKY']}")
        
        # 강수 형태
        if 'PTY' in val and val['PTY']:
          try:
            pty_temp = pyt_code[int(val['PTY'])]
            features['rain'] = pty_temp
            template += pty_temp
            # 강수 있는 경우
            if 'RN1' in val and val['RN1'] != '강수없음':
              rn1_temp = val['RN1']
              # template += f"시간당 {rn1_temp}mm "
              features['rain'] = rn1_temp
          except (ValueError, KeyError):
            print(f"강수 형태 코드 처리 오류: {val['PTY']}")
        
        # 기온
        if 'T1H' in val and val['T1H']:
          try:
            t1h_temp = float(val['T1H'])
            # template += f" 기온 {t1h_temp}℃ "
            features['temp'] = t1h_temp
          except ValueError:
            print(f"기온 값 처리 오류: {val['T1H']}")
        
        # 습도
        if 'REH' in val and val['REH']:
          try:
            reh_temp = float(val['REH'])
            # template += f"습도 {reh_temp}% "
            features['humidity'] = reh_temp
          except ValueError:
            print(f"습도 값 처리 오류: {val['REH']}")
        
        # 풍향/ 풍속
        if 'VEC' in val and val['VEC'] and 'WSD' in val and val['WSD']:
          try:
            vec_temp = deg_to_dir(float(val['VEC']))
            wsd_temp = val['WSD']
            # template += f"풍속 {vec_temp} 방향 {wsd_temp}m/s"
            features['wind_direction'] = vec_temp
            features['wind_speed'] = wsd_temp
          except ValueError:
            print(f"풍향/풍속 값 처리 오류: VEC={val.get('VEC')}, WSD={val.get('WSD')}")
        
        forecasts.append(template + format_weather_features(features))
      except Exception as e:
        print(f"날씨 정보 처리 중 오류 발생: {e}")
        continue

    if not forecasts:
      return f"{city} {gu} {dong} 지역의 날씨 정보를 생성할 수 없습니다."
    
    print(forecasts)
    return "\n---\n".join(forecasts)
    
  except Exception as e:
    print(f"날씨 API 요청 중 오류 발생: {e}")
    return [f"날씨 정보를 가져오는 중 오류가 발생했습니다: {str(e)}"]
      
if __name__ == "__main__":
  asyncio.run(get_forecast_api("서울", "강남구", "역삼동", 62, 123))