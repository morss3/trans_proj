import os, requests
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

resp = requests.post(
    "https://openrouter.ai/api/v1/embeddings",
    headers={"Authorization": f"Bearer {api_key}", "Content-Type": "application/json"},
    json={"model": "openai/text-embedding-3-small", "input": "тест"},
    timeout=30,
)
print("Статус:", resp.status_code)
data = resp.json()
if resp.status_code == 200:
    vec = data["data"][0]["embedding"]
    print("Размерность:", len(vec))
else:
    print("Ошибка:", data)