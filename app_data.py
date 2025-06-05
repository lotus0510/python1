from datetime import datetime
from zoneinfo import ZoneInfo
def weather_condition(receiver_text):
    """
    氣候提示詞,return True or false
    """
    zh_keywords = [
    "天氣", "氣溫", "溫度", "雨", "晴", "陰", "颱風", "雷", "風", "濕度",
    "氣象", "氣壓", "冷", "熱", "雪", "太陽", "曬", "霧", "霜", "鋒面",
    "寒流", "暖流", "悶熱", "溫差"
    ]
    en_keywords = [
    "weather", "temperature", "rain", "sun", "sunny", "cloud", "cloudy", "storm",
    "typhoon", "thunder", "wind", "humidity", "cold", "hot", "snow", "fog", "frost",
    "pressure", "forecast", "heatwave", "chilly", "warm"
    ]
    ja_keywords = [
    "天気", "気温", "温度", "雨", "晴れ", "曇り", "台風", "雷", "風", "湿度",
    "寒い", "暑い", "雪", "霧", "霜", "気圧", "予報", "日差し", "寒波", "熱波"
    ]
    weather_keywords = zh_keywords + en_keywords + ja_keywords
    return any (keyword in receiver_text for keyword in weather_keywords)

def news_condition(receiver_text):
    """
    新聞提示詞,return True or false
    """
    return "新聞" in receiver_text or "news" in receiver_text.lower()

class PromptBuilder:
    def __init__(self,history_message):
        self.conversation_history = history_message
        self.prompts = [
            "預設繁體中文回答，如有要求可使用其他語言回答，或是根據使用者語言進行變化。",
            "語氣輕鬆自然，像朋友聊天。內容簡單好懂，沒有特殊要求不要有太長的回覆",
            "不要有特殊的格式,不要有奇怪的符號",
            f"現在時間是{datetime.now(ZoneInfo('Asia/Taipei')).strftime('%Y-%m-%d %H:%M:%S')}"
        ]
    def build_prompt(self,user_message,weather_data=None,news_data=None):
        system_instructions = "\n".join(self.prompts)
        if weather_data:
            user_message = f"{weather_data}, {user_message}"
        if news_data:
            user_message = f"{news_data}, {user_message}"
        return f"{system_instructions}\n{self.conversation_history}\nAI:{user_message}"