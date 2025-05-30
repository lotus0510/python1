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