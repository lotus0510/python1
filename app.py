from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage
import weather
from ai_chat import ai_chat

# 建立 Flask 應用程式
app = Flask(__name__)

# 建議改用環境變數管理
line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')

app_type = "main"

def weather_info():
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
    return 'OK'

user_histories = {}
@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    接收使用者訊息後，呼叫 ai_chat 函式取得 AI 回覆，
    並用 LINE Bot 回傳給使用者
    """
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
    
    ai_response_type = ai_chat(contents=f'判段使用者詢問的項目: {received_text}\n回覆:"weather" 或是"other"')
    if ai_response_type.strip().lower() == "weather":
        weather_data = weather_info()
        prompt = f"{base_prompt}\n{weather_data}\nAI:"
    else:
        prompt = base_prompt

    try:
        # 呼叫 AI 取得回覆
        ai_response = ai_chat(prompt)
    except Exception as e:
        # 若呼叫失敗，回傳錯誤訊息給使用者
        ai_response = f"抱歉，AI 服務暫時無法使用，請稍後再試。\n{e}"

    # 把 AI 回覆加入歷史，方便下一輪繼續對話
    user_histories[user_id].append(f"AI: {ai_response}")

    # 限制歷史訊息長度，避免無限累積造成負擔
    max_history = 10  # 保留最近10輪對話
    # 一輪包含使用者和AI各一條訊息，總共20條
    if len(user_histories[user_id]) > max_history * 2:
        user_histories[user_id] = user_histories[user_id][-max_history * 2:]


    if "test001" in received_text:
        send_text = f"{ai_response},ai_response_type:{ai_response_type}\n{weather_data}"
    else:
        send_text = ai_response
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=send_text)
    )



if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
