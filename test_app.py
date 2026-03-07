import requests

url = "http://127.0.0.1:8000/generate-learning-path"

payload = {
    "query": "Agentic AI",
    "level": "BEGINNER"
}

response = requests.post(url, json=payload)

print(response.json())