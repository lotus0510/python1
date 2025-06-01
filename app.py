from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import weather
from ai_chat import ai_chat
from sheet import write_to_sheet
import time
import logging
import traceback
import app_data
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
processed_messages = set()
user_histories = {}


# 建立 Flask 應用程式
app = Flask(__name__)

# 建議改用環境變數管理
line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')

def weather_info():
    """
    爬蟲獲取天氣資訊
    """
    weather_data = weather.get_weather_data()
    return weather_data



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
    """
    接收使用者訊息後，呼叫 ai_chat 函式取得 AI 回覆，
    並用 LINE Bot 回傳給使用者
    """
    message_id = event.message.id
    if message_id in processed_messages:
        return
    processed_messages.add(message_id)
    
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

    
    
    base_prompt = app_data.PromptBuilder(history_text)
    # 判斷使用者詢問的項目
    try:
        if app_data.weather_condition(received_text):
            weather_data = weather_info()
            full_prompt = base_prompt.build_prompt(user_message=received_text, weather_data=weather_data)
            
        else:
            full_prompt = base_prompt.build_prompt(user_message=received_text)
        ai_response = ai_chat(full_prompt)
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
    
    try:
        write_to_sheet(
        time_now=time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),
        user_id = event.source.user_id, received_text = received_text, send_text = send_text, time = end_time - start_time,message_id=message_id)
        info = "資料已寫入 Google Sheet"
    except Exception as e:
        logging.exception("寫入 Google Sheet 失敗")
        info = f"寫入 Google Sheet 失敗: {e}\n{traceback.format_exc()}"
    
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=f"{send_text} \n {event.source.user_id} \n 本次花費時間{end_time - start_time:.2f}秒"
                        + f"\n{info}")
    )

    
    
    



if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
