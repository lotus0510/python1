import requests
import json
from collections import defaultdict

def get_weather_data():

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
    url = "https://gnews.io/api/v4/top-headlines"
    params = {
        'lang': 'zh',
        'country': 'tw',
        'token': '5187873e23573c0212fd3db788c9fab2'
    }
    response = requests.get(url, params=params)
    data = response.json()
    return data




if __name__ == "__main__":
    cleaned_data = get_weather_data()
    # 印出適合 AI 使用的 JSON 格式（前 5 筆）
    print(json.dumps(cleaned_data[:5], indent=2, ensure_ascii=False))