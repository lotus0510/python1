import requests

def ai_chat(contents):
    url = "https://openrouter.ai/api/v1/chat/completions"
    headers = {
        "Authorization": "Bearer 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",
        "Content-Type": "application/json"
    }

    data = {
        "model": "deepseek/deepseek-chat-v3-0324:free",  # 或 "anthropic/claude-3-haiku", "mistral/mistral-7b-instruct" 等
        "messages": [
            {"role": "user", "content": contents}
        ]
    }

    response = requests.post(url, headers=headers, json=data)
    return(response.json())

if __name__ == "__main__":
    print(ai_chat("你好！幫我寫一首詩。"))