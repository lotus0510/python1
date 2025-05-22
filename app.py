from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

# 建立 Flask 應用程式
app = Flask(__name__)

# 建議改用環境變數管理
line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')

def ai_chat(contents: str) -> str:
    """
    呼叫 Google Gemini API 取得 AI 回覆
    - contents: 傳入要讓 AI 回答的提示文字
    - 回傳 AI 回覆文字
    """
    gemini_key = 'AIzaSyD2Ce5f2yJ1oBJ0juuDIPuciQySkTg0uVk'
    from google import genai

    client = genai.Client(api_key=gemini_key)
    
    # 呼叫 Gemini 模型生成文字
    response = client.models.generate_content(
        model="gemini-2.0-flash", 
        contents=contents
    )
    
    return response.text


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


@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    """
    接收使用者訊息後，呼叫 ai_chat 函式取得 AI 回覆，
    並用 LINE Bot 回傳給使用者
    """
    received_text = event.message.text

    # 你可以在這裡加上系統提示詞，讓 AI 回答更符合需求
    prompt = f"請用繁體中文回覆，依台北地區，語氣輕鬆自然，像朋友聊天。內容簡單好懂，適合用在 LINE 裡顯示，不要 Markdown。以下是使用者的訊息：{received_text}"

    try:
        ai_response = ai_chat(prompt)
    except Exception as e:
        # 若呼叫 AI 失敗，回覆錯誤訊息
        ai_response = "抱歉，AI 服務暫時無法使用，請稍後再試。"

    # 回覆給使用者
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=ai_response)
    )


if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)
