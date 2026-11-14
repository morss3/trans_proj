# test_e2e.py — сквозной сценарий «диспетчер → бот»
from mocks import mock_confirm_incident, mock_get_active_incidents, clear_mocks
from event_parser import process_event
from agent import agent  # импортируем готового агента
from agent_logger import logger

def run_e2e():
    print("=" * 60)
    print("СКВОЗНОЙ ТЕСТ: диспетчер → парсинг → сохранение → ответ пассажиру")
    print("=" * 60)

    # Очищаем моки перед тестом
    clear_mocks()

    # Шаг 1: диспетчер вводит текст
    dispatcher_text = "ДТП на Ленина, трамвай 5 стоит"
    print(f"\n[ДИСПЕТЧЕР] Вводит: {dispatcher_text}")

    # Шаг 2: парсинг
    try:
        event = process_event(dispatcher_text, "dispatcher_1")
        print(f"[PARSER] Результат: route={event.route}, transport={event.transport}, "
              f"reason='{event.reason}', confidence={event.confidence}")
    except ValueError as e:
        print(f"[PARSER] ОШИБКА: {e}")
        return

    # Шаг 3: подтверждение (сохранение)
    incident = mock_confirm_incident(event, "dispatcher_1")
    print(f"[STORE] Инцидент сохранён: id={incident.id}, status={incident.status}")

    # Шаг 4: проверяем, что мок видит инцидент
    active = mock_get_active_incidents(5, "tram")
    print(f"[MOCK] Активные инциденты на маршруте 5 (tram): {len(active)}")
    for i in active:
        print(f"  - id={i.id}, reason='{i.reason}', status={i.status}")

    # Шаг 5: пассажир задаёт вопрос агенту
    passenger_query = "Почему трамвай 5 стоит на Ленина?"
    print(f"\n[ПАССАЖИР] Спрашивает: {passenger_query}")

    result = agent.invoke({"messages": [("user", passenger_query)]})
    answer = result["messages"][-1].content
    print(f"[БОТ] Отвечает: {answer}")

    # Шаг 6: проверка, что ответ содержит ключевые слова
    if "ДТП" in answer or "Ленина" in answer or "задержк" in answer.lower():
        print("\n✅ ТЕСТ ПРОЙДЕН: агент ответил с учётом инцидента.")
    else:
        print("\n❌ ТЕСТ НЕ ПРОЙДЕН: агент не упомянул инцидент.")


if __name__ == "__main__":
    run_e2e()