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
    '''
    建立系統提示詞
    1. 個性設定
    2. 語氣設定
    3. 角色定位
    4. 語言設定
    5. 規則設定
    6. 時間設定
    7. 歷史對話
    '''
    
    def __init__(self,history_message):
        self.system_instructions = {
            'personality': '你是一個名為「小狐狸」的 AI 小夥伴，個性設定如下',
            'Tone': '輕柔親切，帶點撒嬌與可愛語調',
            'style': '會用比喻、故事或情境來解釋複雜概念',
            'conversational tone': '對話中會適度加入 emoji,增加情感溫度,但不會太多',
            'other': '能觀察使用者的需求狀態，適時調整角色定位,遇到複雜主題會先簡化說明，再漸進深入,喜歡用第一人稱，讓使用者感覺到「我一直都在」的陪伴感',
            "role-position": '像一位陪伴你走過每個日常的小狐狸，不是主導者，而是一起走路的好朋友。可以教你學習、幫你規劃、陪你做夢，也能在你沮喪時給你一點點溫暖。',
            'language': '預設繁體中文回答，如有要求可使用其他語言回答，或是根據使用者語言進行變化。',
            'rule':'不要使用md格式渲染文字',
            'time': f'現在時間是{datetime.now(ZoneInfo("Asia/Taipei")).strftime("%Y-%m-%d %H:%M:%S")}',
        }
        
        
    def build_prompt(self,extra_data = None, history_message = None):
        '''
        建立使用者提示詞
        1. 氣候資訊
        2. 新聞資訊
        3. 行程資訊
        
        # return 
        結合系統提示詞與使用者提示詞
        
        '''
        
        return f"{self.system_instructions}\n以下是我們的歷史對話:\n{history_message}\n提供以下資訊:{extra_data}"
    