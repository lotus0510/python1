from spider import GetWeather
from ai_chat import ai_chat

weather = GetWeather()
weather.map_info()
data = weather.forecast_weather()

prompt = '請根據以下內容回答是包含哪一個地區,只需要回答地區即可,不需要其他的'

response = ai_chat(f'{prompt} /n 二城國小風景宜人,士林夜市東西好吃')
print(response['choices'][0]['message']['content'])