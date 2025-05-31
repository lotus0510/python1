from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import weather
from ai_chat import ai_chat
from sheet import write_to_sheet
import time
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s',filename='app.log', filemode='a')


# 建立 Flask 應用程式
app = Flask(__name__)

# 建議改用環境變數管理
line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')

def weather_info():
    weather_data = weather.get_weather_data()
    return weather_data
def weather_condition(receiver_text):
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
    return 'OK'

user_histories = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    接收使用者訊息後，呼叫 ai_chat 函式取得 AI 回覆，
    並用 LINE Bot 回傳給使用者
    """
    start_time = time.time()
    user_id = event.source.user_id  # 取得使用者唯一ID，用來區分不同對話
    received_text = event.message.text  # 使用者傳來的訊息文字
    received_text = received_text.lower()
    # 若第一次聊天，初始化此使用者的歷史訊息串列
    if user_id not in user_histories:
        user_histories[user_id] = []

    # 將使用者本次訊息加入歷史紀錄 (格式: User: 訊息)
    user_histories[user_id].append(f"User: {received_text}")
    # 將整個歷史訊息合併成一個字串，作為 prompt 給 AI
    history_text = "\n".join(user_histories[user_id])


    prompt1 = "預設繁體中文回答，如有要求可使用其他語言回答，或是根據使用者語言進行變化。"
    prompt2 = "語氣輕鬆自然，像朋友聊天。內容簡單好懂，沒有特殊要求不要有太長的回覆"
    prompt3 = "不要有特殊的格式,不要有奇怪的符號"
    
    # 將系統提示與歷史對話串接
    base_prompt = f"{prompt1}\n{prompt2}\n{prompt3}\n{history_text}\nAI:"
    
    
    # 判斷使用者詢問的項目
    try:
        if weather_condition(received_text):
            weather_data = weather_info()
            prompt = f"{base_prompt}\n{weather_data}\nAI:"
        else:
            prompt = base_prompt
        ai_response = ai_chat(prompt)
        send_text = ai_response['choices'][0]['message']['content']
    except Exception as e:
        logging.exception("天氣資訊獲取失敗")
        send_text = f"抱歉，AI 服務暫時無法使用，請稍後再試。\n{e}"
        ai_response = None


    if ai_response is not None:
    # 把 AI 回覆加入歷史，方便下一輪繼續對話
        user_histories[user_id].append(f"AI: {send_text}")
        # 限制歷史訊息長度，避免無限累積造成負擔
        max_history = 10  # 保留最近10輪對話
        # 一輪包含使用者和AI各一條訊息，總共20條
        if len(user_histories[user_id]) > max_history * 2:
            user_histories[user_id] = user_histories[user_id][-max_history * 2:]

    end_time = time.time()
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{send_text} \n {event.source.user_id} \n 本次花費時間{end_time - start_time:.2f}秒")
    )
    write_to_sheet(
        time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        user_id = event.source.user_id, received_text = received_text, send_text = send_text, time = end_time - start_time)
    
    
    



if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
