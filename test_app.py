import requests

url = "http://127.0.0.1:8000/generate-learning-path"

payload = {
    "query": "Agentic AI",
    "level": "BEGINNER",
    "duration" : "4 Weeks"
}

response = requests.post(url, json=payload)

print(response.json())