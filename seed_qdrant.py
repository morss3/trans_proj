# seed_qdrant.py
from langchain_qdrant import QdrantVectorStore
from langchain_openai import OpenAIEmbeddings
from qdrant_client import QdrantClient
from qdrant_client.http.models import Distance, VectorParams
from langchain_core.documents import Document

# 1. Подключаемся к Qdrant
client = QdrantClient(url="http://localhost:6333", timeout = 30)

# 2. Создаём коллекцию (размерность 1536 для эмбеддингов OpenAI-совместимых моделей)
collection_name = "incidents"
if client.collection_exists(collection_name):
    client.delete_collection(collection_name)
client.create_collection(
    collection_name=collection_name,
    vectors_config=VectorParams(size=384, distance=Distance.COSINE),
)

# 3. Создаём эмбеддинги (используем ту же модель, что и для LLM, или отдельную)
# Для простоты используем эмбеддинги через OpenRouter (если поддерживаются) или заглушку.
# ВАЖНО: Если OpenRouter не даёт эмбеддинги, используй другую модель, например, из sentence-transformers.
# Пока для теста можно использовать простую модель, но для реального RAG нужна нормальная.
# Здесь мы предполагаем, что у тебя есть доступ к эмбеддингам через OpenAI-совместимый API.
# Если нет — временно замени на любую локальную модель.
from langchain_core.embeddings import Embeddings
from openrouter import OpenRouter
import os

class OpenRouterEmbeddings(Embeddings):
    def __init__(self):
        self.client = OpenRouter(api_key=os.getenv("OPENROUTER_API_KEY"))
    
    def embed_documents(self, texts):
        # OpenRouter SDK обычно обрабатывает по одному тексту за раз, можно перебирать в цикле
        return [self._embed(text) for text in texts]
    
    def embed_query(self, text):
        return self._embed(text)
    
    def _embed(self, text):
        res = self.client.embeddings.generate(
            input=text, 
            model="openai/text-embedding-3-small"
        )
        # Возвращаемый формат нужно скорректировать в соответствии с реальным ответом SDK
        return res.data[0].embedding
    
from langchain_huggingface import HuggingFaceEmbeddings

embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)
# 4. Создаём векторное хранилище и добавляем документы
vector_store = QdrantVectorStore(
    client=client,
    collection_name=collection_name,
    embedding=embeddings,
)

docs = [
    Document(page_content="ДТП на проспекте Ленина. Трамвай маршрута 5 стоит. Ожидаемое восстановление 20 минут.", metadata={"route": 5, "transport": "tram"}),
    Document(page_content="Плановые работы на путях. Автобус 10 следует с задержкой 15 минут.", metadata={"route": 10, "transport": "bus"}),
    Document(page_content="На маршруте 5 автобусов задержек нет, движение в штатном режиме.", metadata={"route": 5, "transport": "bus"}),
]
vector_store.add_documents(docs)
print("Данные загружены в Qdrant.")