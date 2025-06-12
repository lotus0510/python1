import requests
import json
from collections import defaultdict
from geopy.geocoders import Nominatim
import datetime
from zoneinfo import ZoneInfo
def get_weather_data():
    '''
    回傳整理後的氣候資訊
    1. 氣溫
    2. 降雨機率
    3. 降雨量
    4. 風速
    5. 風向
    6. 氣壓
    '''
    weather_api = 'https://opendata.cwa.gov.tw/api/v1/rest/datastore/F-D0047-063?Authorization=CWA-62076E77-DFB8-4CF7-B144-8C46A65B10C4'

    cleaned_data = []
    response = requests.get(weather_api)
    data = response.json()

    # 遍歷所有地區
    locations = data['records']['Locations']
    for city in locations:
        city_name = city['LocationsName']
        for loc in city['Location']:
            district = loc['LocationName']
            element_map = defaultdict(dict)

            for element in loc['WeatherElement']:
                element_name = element['ElementName']
                for entry in element['Time']:
                    start = entry['StartTime'][:16].replace('T', ' ')
                    end = entry['EndTime'][:16].replace('T', ' ')
                    key = (start, end)
                    value_dict = entry['ElementValue'][0]
                    # 有些是 {"Value": "25"}，有些是 {"MaxTemperature": "25"}
                    value = list(value_dict.values())[0]
                    element_map[key][element_name] = value

            for (start, end), values in element_map.items():
                row = {
                    "縣市": city_name,
                    "地區": district,
                    "起始時間": start,
                    "結束時間": end
                }
                row.update(values)
                cleaned_data.append(row)
    return cleaned_data

def get_news_data():
    '''
    回傳原始的新聞資訊
    1. 新聞標題
    2. 新聞內容
    3. 新聞來源
    '''
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        'lang': 'zh',
        'country': 'tw',
        'token': '5187873e23573c0212fd3db788c9fab2'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data

class GetWeather:
    
    '''
    1. 使用 Google Weather API 獲取氣候資訊
    2. 預設士林地區
    3. 可透過self.location 修改地區名稱
    4. 使用map_info()獲取資訊並查詢
    5. 回傳true或false
    6. 成功或失敗都將存入self.response,(建議查看T/F確認狀態成功或失敗)
    '''
    def __init__(self):
        self.base_url = "https://weather.googleapis.com/v1/currentConditions:lookup"
        self.forecast_url = 'https://weather.googleapis.com/v1/forecast/hours:lookup'

        self.key = 'AIzaSyAqZELHTTfH28aVX2-b3hQRgW_y4R3Cvi0'
        self.location = '士林'
        self.latitude = None
        self.longitude = None
    def map_info(self):
        # 初始化地理定位器
        geolocator = Nominatim(user_agent="myapp")
        try:
            # 查詢地址座標，附加「台灣」以協助精準定位
            location = geolocator.geocode(f"{self.location}, 台灣")
            
            if location:
                self.latitude = location.latitude
                self.longitude = location.longitude
                self.get_google_weather()
            else:
                self.summary = f"無法找到地址: {self.location}"
                return False
            
        except Exception as e:
            self.summary = f"地理定位錯誤: {(e)}"
            return False
        
    def get_google_weather(self):
        self.params = {
            'key' : self.key,
            'location.latitude': self.latitude,
            'location.longitude' : self.longitude
        }
        self.response = requests.get(self.base_url, params=self.params)

    def weather_summary(self):
        """
        解析 self.response 並回傳一份格式化後的中文天氣摘要。
        """
        # 使用 .get() 方法安全地提取資料，避免因缺少鍵而引發錯誤
        data = self.response.json()

        # --- 時間與地點 ---
        tz_id = data.get('timeZone', {}).get('id', '未知時區')
        try:
            utc_time_str = data.get('currentTime', '')
            utc_dt = datetime.datetime.fromisoformat(utc_time_str.replace('Z', '+00:00'))
            local_tz = ZoneInfo(tz_id)
            local_dt = utc_dt.astimezone(local_tz)
            formatted_time = local_dt.strftime('%Y-%m-%d %p %I:%M')
        except (ValueError, KeyError) as e:
            # 將捕捉到的錯誤物件 e 印出來
            print(f"!!! 捕獲到時間轉換錯誤，詳細資訊: {e}")
            formatted_time = "時間格式錯誤"
        
        # --- 主要天氣資訊 ---
        weather_desc = data.get('weatherCondition', {}).get('description', {}).get('text', 'N/A')
        temp = data.get('temperature', {}).get('degrees', 'N/A')
        feels_like = data.get('feelsLikeTemperature', {}).get('degrees', 'N/A')
        humidity = data.get('relativeHumidity', 'N/A')
        rain_prob = data.get('precipitation', {}).get('probability', {}).get('percent', 'N/A')
        thunder_prob = data.get('thunderstormProbability', 'N/A')

        # --- 風力資訊 ---
        wind_speed = data.get('wind', {}).get('speed', {}).get('value', 'N/A')
        wind_gust = data.get('wind', {}).get('gust', {}).get('value', 'N/A')
        wind_cardinal = data.get('wind', {}).get('direction', {}).get('cardinal', 'N/A')

        # --- 其他專業資訊 ---
        visibility = data.get('visibility', {}).get('distance', 'N/A')
        pressure = data.get('airPressure', {}).get('meanSeaLevelMillibars', 'N/A')
        uv_index = data.get('uvIndex', 0)
        is_daytime = data.get('isDaytime', False)
        uv_note = f"({ '白天' if is_daytime else '晚上，無紫外線' })"
        
        # --- 使用 f-string 組裝成易讀的報告 ---
        self.summary = (
            f"--- {self.location}即時天氣報告 ---\n"
            f"📍 地點：{tz_id}\n"
            f"🕒 時間：{formatted_time}\n"
            f"--------------------------\n"
            f"☀️ 天氣：{weather_desc}\n"
            f"🌡️ 溫度：{temp}°C\n"
            f"🥵 體感：{feels_like}°C\n"
            f"💧 濕度：{humidity}%\n"
            f"☔️ 降雨機率：{rain_prob}%\n"
            f"⚡️ 雷雨機率：{thunder_prob}%\n"
            f"💨 風速：每小時 {wind_speed} 公里 (最大陣風 {wind_gust} 公里)，{wind_cardinal} 風\n"
            f"👁️ 能見度：{visibility} 公里\n"
            f"📈 氣壓：{pressure} hPa\n"
            f"😎 紫外線指數：{uv_index} {uv_note}\n"
        )
        return True
    def forecast_weather(self):
        '''
        return data(json)
        回傳原始資料
        '''
        
        params = {
        'key': self.key,
        'location.latitude': self.latitude,
        'location.longitude': self.longitude,
        'hours': 24
    }
        response = requests.get(self.forecast_url,params=params)
        data = response.json()
        return data


if __name__ == "__main__":
    cleaned_data = get_weather_data()
    # 印出適合 AI 使用的 JSON 格式（前 5 筆）
    print(json.dumps(cleaned_data[:5], indent=2, ensure_ascii=False))