import requests

ACCESS_TOKEN = 'cu72CgnyjjlIHApWysa0NSyC0KVlp6+WGUfxMdlMH7g7muGvSAPzr2zXAsgBiS9yEkNuOoAoePqzB08Sho+9/9L/A74UFR+Pw8C2ghER9vDbqH7ky4TgctUBr321/OoNML2oAI9BC/QfmmuWaowMegdB04t89/1O/w1cDnyilFU='

headers = {
    'Content-Type': 'application/json',
    'Authorization': f'Bearer {ACCESS_TOKEN}'
}

data = {
    "messages": [
        {
            "type": "text",
            "text": "這是從 Python 傳來的 LINE Bot 訊息！"
        }
    ]
}

url = "https://api.line.me/v2/bot/message/broadcast"  # 改成 broadcast

response = requests.post(url, headers=headers, json=data)

if response.status_code == 200:
    print("✅ 已成功傳送訊息！")
else:
    print(f"❌ 傳送失敗，狀態碼：{response.status_code}")
    print("錯誤訊息：", response.text)
