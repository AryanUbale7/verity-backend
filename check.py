import requests

API_KEY = "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"

url = "https://openrouter.ai/api/v1/chat/completions"

headers = {
    "Authorization": f"Bearer {API_KEY}",
    "Content-Type": "application/json"
}

data = {
    "model": "mistralai/mixtral-8x7b-instruct",
    "messages": [
        {"role": "user", "content": "What is 2+2?"}
    ]
}

response = requests.post(url, headers=headers, json=data)

print(response.json())