# agent.py
from langchain_core.tools import tool
from langgraph.prebuilt import create_react_agent
from core.settings import create_openrouter_model
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings

# 1. Подключаемся к Qdrant
import os
# Заставить localhost обходить прокси, но не влиять на внешние запросы (OpenRouter)
os.environ["NO_PROXY"] = "localhost,127.0.0.1"

client = QdrantClient(
    host="localhost",
    port=6333,
    timeout=60,
    prefer_grpc=False,
    check_compatibility=False
)
# 2. Те же эмбеддинги, что и в seed_qdrant.py (размерность 384!)
embeddings = HuggingFaceEmbeddings(
    model_name="intfloat/multilingual-e5-small",
    model_kwargs={'device': 'cpu'},
    encode_kwargs={'normalize_embeddings': True}
)

vector_store = QdrantVectorStore(
    client=client,
    collection_name="incidents",
    embedding=embeddings,
)

# 2. Определяем инструмент (tool), который агент сможет вызывать
@tool
def search_incidents(query: str) -> str:
    """Ищет информацию об инцидентах на транспорте в базе знаний."""
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "В базе нет информации по этому запросу."
    return "\n".join([
        f"[Маршрут {doc.metadata.get('route')}, {doc.metadata.get('transport')}] {doc.page_content}"
        for doc in results
    ])
# 3. Создаём LLM и агента
llm = create_openrouter_model()
tools = [search_incidents]
agent = create_react_agent(llm, tools)

# 4. Тестируем
if __name__ == "__main__":
    query = "Почему трамвай 1 стоит на Пушкина?"
    print(f"Вопрос: {query}")
    result = agent.invoke({"messages": [("user", query)]})
    print("Ответ агента:", result["messages"][-1].content)