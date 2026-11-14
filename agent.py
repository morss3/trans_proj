# agent.py
from langchain_core.tools import tool
from langchain.agents import create_agent
from core.settings import create_openrouter_model
from langchain_qdrant import QdrantVectorStore
from qdrant_client import QdrantClient
from langchain_huggingface import HuggingFaceEmbeddings
from mocks import mock_get_active_incidents, mock_get_all_active_incidents
# 1. Подключаемся к Qdrant
import os

from agent_logger import LoggingMiddleware, logger

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
    """Ищет информацию об инцидентах на транспорте в базе знаний.
    Используй, когда пользователь спрашивает ПРО ПРИЧИНУ, МЕСТО или ОБЩУЮ информацию,
    а не про конкретный маршрут."""
    
    results = vector_store.similarity_search(query, k=2)
    if not results:
        return "В базе нет информации по этому запросу."
    return "\n".join([
        f"[Маршрут {doc.metadata.get('route')}, {doc.metadata.get('transport')}] {doc.page_content}"
        for doc in results
    ])

@tool
def get_active_incidents(route: int, transport: str) -> str:
    """Возвращает активные инциденты по маршруту и типу транспорта.
    Используй, когда пользователь явно указал номер маршрута и тип транспорта."""
    print(f"[DEBUG] get_active_incidents вызван с route={route}, transport={transport}")
    incidents = mock_get_active_incidents(route, transport)  # пока мок
    if not incidents:
        return f"На маршруте {route} ({transport}) активных задержек нет."
    return "\n".join([
        f"Маршрут {i.route} ({i.transport}): {i.reason}"
        for i in incidents
    ])

@tool
def get_all_active_incidents() -> str:
    """Возвращает ВСЕ активные инциденты в городе (без фильтра по маршруту).
    Используй, когда пользователь спрашивает общую картину:
    'какие сейчас задержки?', 'покажи текущие инциденты', 'что происходит на транспорте?',
    'что случилось на <улица>?' (если маршрут не указан)."""
    print("[DEBUG] get_all_active_incidents вызван")
    incidents = mock_get_all_active_incidents()
    if not incidents:
        return "В городе нет активных задержек."
    return "\n".join([
        f"Маршрут {i.route} ({i.transport}): {i.reason}"
        for i in incidents
    ])
# 3. Создаём LLM и агента

SYSTEM_PROMPT = """Ты — диспетчер транспортной системы.
Отвечай только на основе данных из инструментов.
Не выдумывай маршруты и причины. Не давай советов вне транспортной темы.
Будь краток и вежлив.

Правила выбора инструмента:
1. Если пользователь указал конкретный маршрут и тип транспорта — используй get_active_incidents(route, transport).
2. Если пользователь спрашивает общую картину ('какие сейчас задержки?', 'что случилось на Ленина?') — сначала используй get_all_active_incidents (SQLite — оперативный реестр).
3. Если в SQLite нет активного инцидента, но вопрос про причину/место/FAQ — используй search_incidents (Qdrant — база знаний).
4. Если get_active_incidents или get_all_active_incidents вернули инцидент — это официальный источник истины.
5. Если search_incidents находит текст, но SQLite говорит 'нет задержек' — доверяй SQLite (актуальный статус).
6. Как только получил результат от инструмента — сразу дай финальный ответ. Не вызывай инструменты повторно, если уже есть результат.
"""

llm = create_openrouter_model()
tools = [search_incidents, get_active_incidents, get_all_active_incidents]
agent = create_agent(llm, tools, system_prompt = SYSTEM_PROMPT, middleware=[LoggingMiddleware()]).with_config({"recursion_limit":15})
# print(agent.get_graph().draw_mermaid())

# 4. Тестируем
if __name__ == "__main__":
    logger.info("=== START AGENT ===") 
    query = "Когда пятый трамвай уже приедет? я пять лет уже стою на остановке жду, что за хрень!"
    # query = "Что известно о текущих инцидентах?"
    logger.info(f"USER_QUERY | {query}")
    print(f"Вопрос: {query}")

    result = agent.invoke({"messages": [("user", query)]})

    answer = result["messages"][-1].content
    logger.info(f"FINAL_ANSWER | {answer}")
    print("Ответ агента:", answer)