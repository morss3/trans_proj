"""
contracts.py — Единый контракт между модулями проекта.
Команда из 4 человек работает параллельно против этих сигнатур.
Моки (заглушки) создаются в отдельных файлах, реальные реализации — в своих модулях.
"""

from dataclasses import dataclass, field
from typing import Literal, Optional
from datetime import datetime


# ============================================================
# ОБЩИЕ ТИПЫ ДАННЫХ (используются всеми модулями)
# ============================================================

Platform = Literal["telegram", "vk"]
TransportType = Literal["bus", "tram", "trolleybus"]
IncidentStatus = Literal["active", "resolved"]


@dataclass
class Incident:
    """Структурированное событие (инцидент) в БД."""
    id: Optional[int] = None
    route: int = 0
    transport: TransportType = "bus"
    reason: str = ""
    status: IncidentStatus = "active"
    start_time: datetime = field(default_factory=datetime.now)
    expected_end_time: Optional[datetime] = None
    dispatcher_id: str = ""


@dataclass
class ParsedEvent:
    """Результат парсинга свободного текста диспетчера (ещё не подтверждён)."""
    route: int
    transport: TransportType
    reason: str
    confidence: float  # 0.0–1.0, насколько LLM уверена в разборе
    raw_text: str


@dataclass
class Subscription:
    """Подписка пользователя на маршрут."""
    user_id: str
    platform: Platform
    route: int
    transport: TransportType


@dataclass
class AgentResponse:
    """Ответ ядра пользователю (в мессенджер)."""
    text: str
    escalated: bool = False  # True, если создан тикет оператору
    ticket_id: Optional[int] = None


# ============================================================
# КОНТРАКТ 1: Ядро ↔ Мессенджеры (Telegram, ВК)
# Владелец: Человек 1 (ядро) вызывает, Человек 3 (мессенджеры) реализует адаптер.
# ============================================================

def ask(user_id: str, platform: Platform, text: str) -> AgentResponse:
    """
    Принимает вопрос пассажира, возвращает ответ ядра.

    :param user_id: ID пользователя в мессенджере
    :param platform: "telegram" или "vk"
    :param text: текст вопроса от пассажира
    :return: AgentResponse с текстом ответа и флагом эскалации
    """
    raise NotImplementedError


def notify_subscribers(route: int, transport: TransportType, message: str) -> int:
    """
    Рассылает уведомление подписчикам маршрута.
    Вызывает ядро (Человек 1) после подтверждения инцидента.
    Реализует Человек 3 (мессенджеры).

    :param route: номер маршрута
    :param transport: тип транспорта
    :param message: текст уведомления
    :return: число успешно отправленных сообщений
    """
    raise NotImplementedError


# ============================================================
# КОНТРАКТ 2: Ядро ↔ Админка диспетчера
# Владелец: Человек 2 (админка) вызывает, Человек 1 (ядро) реализует парсер.
# ============================================================

def process_event(raw_text: str, dispatcher_id: str) -> ParsedEvent:
    """
    Принимает свободный текст от диспетчера, возвращает структурированное событие.
    LLM раскладывает текст в поля (маршрут, транспорт, причина).
    Валидация через Pydantic внутри.

    :param raw_text: например, "ДТП на Ленина, трамвай 5 стоит"
    :param dispatcher_id: ID диспетчера (для аудита)
    :return: ParsedEvent с распарсенными полями и confidence
    :raises ValueError: если не удалось распарсить маршрут/транспорт
    """
    raise NotImplementedError


def confirm_incident(event: ParsedEvent, dispatcher_id: str) -> Incident:
    """
    Записывает подтверждённый диспетчером инцидент в SQLite.
    После записи ядро вызывает notify_subscribers().

    :param event: подтверждённое событие из process_event()
    :param dispatcher_id: кто подтвердил
    :return: Incident с присвоенным id
    """
    raise NotImplementedError


def resolve_incident(incident_id: int, dispatcher_id: str) -> Incident:
    """
    Закрывает инцидент (status="resolved").

    :param incident_id: ID инцидента в БД
    :param dispatcher_id: кто закрыл
    :return: обновлённый Incident
    """
    raise NotImplementedError


# ============================================================
# КОНТРАКТ 3: Ядро ↔ Реляционная БД (SQLite)
# Владелец: Человек 1 (ядро) вызывает, Человек 4 (данные/инфра) реализует репозиторий.
# ============================================================

def get_active_incidents(route: int, transport: TransportType) -> list[Incident]:
    """
    Возвращает активные инциденты по маршруту и типу транспорта.
    Вызывается через Function Calling из LLM.

    :param route: номер маршрута
    :param transport: тип транспорта
    :return: список активных Incident (пустой, если нет)
    """
    raise NotImplementedError


def get_schedule(route: int, transport: TransportType) -> list[dict]:
    """
    Возвращает расписание маршрута (если есть в БД).

    :return: список словарей вида {"stop": str, "time": str}
    """
    raise NotImplementedError


def create_ticket(user_id: str, platform: Platform, text: str) -> int:
    """
    Создаёт тикет для оператора (эскалация).
    Вызывается ядром, когда LLM не уверена или пользователь недоволен.

    :return: ID созданного тикета
    """
    raise NotImplementedError


# ============================================================
# КОНТРАКТ 4: Ядро ↔ Векторная БД (Qdrant) — RAG
# Владелец: Человек 1 (ядро) вызывает, Человек 4 (данные/инфра) реализует.
# ============================================================

def rag_search(query: str, top_k: int = 5, filters: Optional[dict] = None) -> list[dict]:
    """
    Семантический поиск по базе знаний и текстам инцидентов.

    :param query: вопрос пользователя
    :param top_k: сколько результатов вернуть
    :param filters: например, {"route": 5, "transport": "tram"}
    :return: список словарей {"text": str, "score": float, "metadata": dict}
    """
    raise NotImplementedError


# ============================================================
# КОНТРАКТ 5: Подписки (SQLite)
# Владелец: Человек 3 (мессенджеры) вызывает, Человек 4 (данные) реализует.
# ============================================================

def add_subscription(user_id: str, platform: Platform, route: int, transport: TransportType) -> bool:
    """Добавляет подписку. Возвращает True, если добавлена (не дубль)."""
    raise NotImplementedError


def remove_subscription(user_id: str, platform: Platform, route: int) -> bool:
    """Удаляет подписку. Возвращает True, если была."""
    raise NotImplementedError


def list_subscriptions(user_id: str, platform: Platform) -> list[Subscription]:
    """Возвращает список подписок пользователя."""
    raise NotImplementedError


# ============================================================
# КОНТРАКТ 6: Голосовой ввод (STT) — админка
# Владелец: Человек 2 (админка) реализует.
# ============================================================

def transcribe_audio(audio_bytes: bytes, language: str = "ru") -> str:
    """
    Распознаёт речь из аудио в текст (Speech-to-Text).
    Используется в админке для голосового ввода диспетчера.

    :param audio_bytes: сырые байты аудио (ogg/wav)
    :param language: язык распознавания
    :return: распознанный текст
    """
    raise NotImplementedError