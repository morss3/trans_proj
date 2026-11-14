# event_parser.py
from langchain_core.prompts import ChatPromptTemplate
from pydantic import BaseModel, Field
from contract import ParsedEvent, TransportType
from core.settings import create_openrouter_model
# идея: если тип маршрута не указан, а номер есть, найти по базе знаний, что это за маршрут (bus/tram/trolleybus). Пока оставим как есть.
class ParsedEventSchema(BaseModel):
    """Схема для structured output (то, что LLM должна вернуть)."""
    route: int = Field(description="Номер маршрута (целое число). 0, если не распознан.")
    transport: TransportType = Field(description="Тип транспорта: bus, tram или trolleybus.Если не указан явно — 'bus'.")
    reason: str = Field(description="Краткая причина инцидента (например, 'ДТП на Ленина').")
    confidence: float = Field(description="Уверенность от 0.0 до 1.0. Ниже 0.5, если маршрут не распознан.")


SYSTEM_PROMPT = """Ты — диспетчер транспортной системы. 
Твоя задача — разобрать свободный текст диспетчера в структурированное событие.

Правила:
1. transport всегда на английском: bus (автобус), tram (трамвай), trolleybus (троллейбус). Если маршрут не указан или не распознан — bus, confidence < 0.5.
2. route — целое число. Если маршрут не указан или не распознан — route=0, confidence < 0.5.
3. reason — краткая причина (например, "ДТП на Ленина", "Плановые работы").
4. confidence — насколько ты уверен в разборе (0.0–1.0). Если что-то не распознано — снижай.
5. Если текст вообще не про инцидент на транспорте — верни route=0, confidence=0.0.

Примеры:
- "ДТП на Ленина, трамвай 5 стоит" → route=5, transport="tram", reason="ДТП на Ленина", confidence=0.95
- "Автобус 10 сломался на Мира" → route=10, transport="bus", reason="Поломка на Мира", confidence=0.9
- "Плановые работы, троллейбус 7" → route=7, transport="trolleybus", reason="Плановые работы", confidence=0.85
"""


def process_event(raw_text: str, dispatcher_id: str) -> ParsedEvent:
    """
    Принимает свободный текст от диспетчера, возвращает структурированное событие.
    
    :param raw_text: например, "ДТП на Ленина, трамвай 5 стоит"
    :param dispatcher_id: ID диспетчера (для аудита)
    :return: ParsedEvent с распарсенными полями
    :raises ValueError: если не удалось распарсить (confidence=0.0 и route=0)
    """
    llm = create_openrouter_model()
    
    # with_structured_output заставляет LLM вернуть JSON, соответствующий схеме
    structured_llm = llm.with_structured_output(ParsedEventSchema)
    
    prompt = ChatPromptTemplate.from_messages([
        ("system", SYSTEM_PROMPT),
        ("user", "Разбери текст диспетчера: {raw_text}")
    ])
    
    chain = prompt | structured_llm
    
    try:
        result: ParsedEventSchema = chain.invoke({"raw_text": raw_text})
    except Exception as e:
        raise ValueError(f"Не удалось распарсить текст: {raw_text}. Ошибка: {e}")
    
    # Если confidence слишком низкий и маршрут не распознан — считаем, что это не инцидент
    if result.confidence < 0.3 and result.route == 0:
        raise ValueError(f"Текст не похож на инцидент: {raw_text}")
    
    return ParsedEvent(
        route=result.route,
        transport=result.transport,
        reason=result.reason,
        confidence=result.confidence,
        raw_text=raw_text
    )


# Для быстрой проверки
if __name__ == "__main__":
    test_texts = [
        "Маршрут задерживается из-за снегопада",
        "Сегодня хорошая погода",  # не инцидент — должен упасть
    ]
    for text in test_texts:
        print(f"\nВход: {text}")
        try:
            event = process_event(text, "dispatcher_test")
            print(f"  → route={event.route}, transport={event.transport}, "
                  f"reason='{event.reason}', confidence={event.confidence}")
        except ValueError as e:
            print(f"  → ОШИБКА: {e}")