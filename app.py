from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import spider
from ai_chat import ai_chat
from google_server import write_to_sheet
import google_server
import time
import logging
import traceback
import app_data
import spider
from enum import Enum

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

class TextType(Enum):
    weather = "weather"
    news = "news"
    calendar = "calendar"
    other = "other"

class VariableManager():
    def __init__(self):
        self.message_id_set = set() # 記錄已處理過的訊息ID
        self.user_histories = {} # 記錄使用者歷史訊息(順便紀錄此id是否有過紀錄)
        
        self.user_id = None # 記錄使用者ID
        self.received_text = None # 記錄使用者傳來的訊息文字
        self.send_text = None # 記錄AI回覆的訊息文字
        self.time = None # 記錄處理時間
        self.message_id = None # 記錄訊息ID
        self.time_now = None # 記錄時間
        self.history_text = None # 記錄歷史訊息
    
    def message_id_check(self, message_id):
        """
        檢查訊息ID是否已處理過
        如果已處理過，則返回True
        如果未處理過，則將訊息ID加入已處理過的集合，並返回False
        """
        
        if message_id in self.message_id_set:
            return True
        else:
            self.message_id_set.add(message_id)
            return False
    def received_text_process(self):
        '''
        處理使用者傳來的訊息文字
        1. 將使用者傳來的訊息文字轉換為小寫
        2. 如果使用者ID不在使用者歷史訊息串列中，則初始化使用者歷史訊息串列
        3. 將使用者本次訊息加入歷史紀錄 (格式: User: 訊息)
        4. 將整個歷史訊息合併成一個字串，作為 prompt 給 AI
        '''
        
        self.received_text = self.received_text.lower() # 將使用者傳來的訊息文字轉換為小寫
        
        # 如果使用者ID不在使用者歷史訊息串列中，則初始化使用者歷史訊息串列
        if self.user_id not in self.user_histories:
            self.user_histories[self.user_id] = []
        
        # 將使用者本次訊息加入歷史紀錄 (格式: User: 訊息)
        self.user_histories[self.user_id].append(f"User: {self.received_text}")
        
        # 將整個歷史訊息合併成一個字串，作為 prompt 給 AI
        self.history_text = "\n".join(self.user_histories[self.user_id])
class ReceivedAnalysis():
    def __init__(self):
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
        self.weather_keywords = zh_keywords + en_keywords + ja_keywords
        self.news_keywords = ["新聞", "news"]
        self.calendar_keywords = ["行程", "schedule", "行程表", "行程規劃", "行程安排",'僅開發者使用功能']
    def received_text_type(self,received_text):
        '''
        判斷使用者傳來的訊息文字屬於哪一種類型
        1. 氣候資訊
        2. 新聞資訊
        3. 行程資訊
        '''
        if any(keyword in received_text for keyword in self.weather_keywords):
            weather_data = spider.get_weather_data()
            return weather_data
        elif any(keyword in received_text for keyword in self.news_keywords):
            news_data = spider.get_news_data()
            return news_data
        elif any(keyword in received_text for keyword in self.calendar_keywords) and manager.user_id == "U82040bf54df534cb1a6935b60f228eaa":
            calendar_data = google_server.get_calendar_events()
            return calendar_data
        else:
            return None
            
            
            
        

manager = VariableManager()
received_analysis = ReceivedAnalysis()
bundle_prompt = app_data.PromptBuilder(manager.history_text)

# 建立 Flask 應用程式
app = Flask(__name__)

# 建議改用環境變數管理
line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')




@app.route("/", methods=['GET'])
def home():
    return "LINE Bot is running."


@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers.get('X-Line-Signature', '')
    body = request.get_data(as_text=True)


    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)
    return 'OK',200

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    manager.message_id = event.message.id
    if manager.message_id_check(manager.message_id):
        return
    
    start_time = time.time()
    """
    接收使用者訊息後，呼叫 ai_chat 函式取得 AI 回覆，
    並用 LINE Bot 回傳給使用者
    """
    manager.user_id = event.source.user_id
    manager.received_text = event.message.text.lower()
    time1 = time.time() # 基礎資訊處理
    
    manager.received_text_process()  # 處理使用者傳來的訊息文字，使其與歷史資訊結合
    time2 = time.time() 
    
    extra_data = received_analysis.received_text_type(manager.received_text)  # 判斷使用者傳來的訊息文字屬於哪一種類型(是否需要額外資訊)
    time3 = time.time()
    
    full_prompt = bundle_prompt.build_prompt(extra_data=extra_data,history_text=manager.history_text)  # 建立使用者提示詞
    time4 = time.time()


    try:        
        ai_response = ai_chat(full_prompt)
        manager.send_text = ai_response['choices'][0]['message']['content']
    except Exception as e:
        logging.exception("資訊獲取失敗")
        manager.send_text = f"抱歉，AI 服務暫時無法使用，請稍後再試。\n{e}"
        ai_response = None
    time5 = time.time()


    if ai_response is not None:
    # 把 AI 回覆加入歷史，方便下一輪繼續對話
        manager.user_histories[manager.user_id].append(f"AI: {manager.send_text}")
        # 限制歷史訊息長度，避免無限累積造成負擔
        max_history = 10  # 保留最近10輪對話
        # 一輪包含使用者和AI各一條訊息，總共20條
        if len(manager.user_histories[manager.user_id]) > max_history * 2:
            manager.user_histories[manager.user_id] = manager.user_histories[manager.user_id][-max_history * 2:]

    time6 = time.time()
    # manager_time={
    #     '基礎資訊處理' : time1 - start_time,
    #     '使用者訊息處理': time2 - time1,    
    #     '判斷使用者傳來的訊息文字屬於哪一種類型': time3 - time2,
    #     '建立使用者提示詞': time4 - time3,
    #     'ai資訊獲取': time5 - time4,
    #     '回覆資訊處理': time6 - time5
    # }
    
    
        
    MAX_CELL_LENGTH = 50000

    def truncate(text):
        return text[:MAX_CELL_LENGTH - 1000] + "...[內容過長已截斷]" if len(text) > MAX_CELL_LENGTH else text

    try:
        write_to_sheet(
            time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
            user_id = manager.user_id,
            received_text = truncate(full_prompt),
            send_text = truncate(manager.send_text),
            time = time6 - start_time,
            message_id=manager.message_id,
            time1=time1-start_time,
            time2 = time2-time1,
            time3 = time3-time2,
            time4 = time4-time3,
            time5 = time5-time4,
            time6 = time6-time5
        )
        info = "資料已寫入 Google Sheet"
    except Exception as e:
        logging.exception("寫入 Google Sheet 失敗")
        info = f"寫入 Google Sheet 失敗: {e}\n{traceback.format_exc()}"

    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{manager.send_text}")
    )

    
    
    



if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
