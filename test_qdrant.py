import os
# Заставить localhost обходить прокси, но не влиять на внешние запросы (OpenRouter)
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

from qdrant_client import QdrantClient

client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=60,
    prefer_grpc=False,
    check_compatibility=False
)

try:
    print("Коллекции:", client.get_collections())
    print("OK")
except Exception as e:
    print("FAIL:", type(e).__name__, e)