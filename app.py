from flask import Flask, request, abort
from linebot import LineBotApi, WebhookHandler
from linebot.exceptions import InvalidSignatureError
from linebot.models import MessageEvent, TextMessage, TextSendMessage

app = Flask(__name__)

line_bot_api = LineBotApi('cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU=')
handler = WebhookHandler('de3344d7fe3af2ae40a4f4d88581fba3')

@app.route("/", methods=['GET'])
def home():
    return "LINE Bot is running."

@app.route("/webhook", methods=['POST'])
def webhook():
    signature = request.headers['X-Line-Signature']
    body = request.get_data(as_text=True)

    try:
        handler.handle(body, signature)
    except InvalidSignatureError:
        abort(400)

    return 'OK'

@handler.add(MessageEvent, message=TextMessage)
def handle_message(event):
    line_bot_api.reply_message(
        event.reply_token,
        TextSendMessage(text=event.message.text)
    )

if __name__ == "__main__":
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

