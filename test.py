import requests

api_key = "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"
headers = {
    "Authorization": f"Bearer {api_key}"
}

response = requests.get("https://openrouter.ai/api/v1/auth/key", headers=headers)
data = response.json()

print(data)
