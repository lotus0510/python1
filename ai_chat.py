import requests

def ai_chat(message):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",  # 或 "anthropic/claude-3-haiku", "mistral/mistral-7b-instruct" 等
        "messages": [
            {"role": "user", "content": message}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return(response.json()['choices'][0]['message']['content'])

if __name__ == "__main__":
    print(ai_chat("你好！幫我寫一首詩。"))