# # mocks.py — заглушки для разработки ядра
# from contract import Incident
# from datetime import datetime, timedelta

# TRANSPORT_MAP = {
#     "трамвай": "tram",
#     "трамваи": "tram",
#     "автобус": "bus",
#     "автобусы": "bus",
#     "троллейбус": "trolleybus",
#     "троллейбусы": "trolleybus",
# }

# def normalize_transport(transport: str) -> str:
#     """Приводит русское/английское название транспорта к каноническому (bus/tram/trolleybus)."""
#     if not transport:
#         return "bus"  # дефолт, если пусто
#     key = transport.strip().lower()
#     return TRANSPORT_MAP.get(key, key)  # если не нашли — возвращаем как есть (вдруг уже "tram")

# def mock_get_active_incidents(route: int, transport: str) -> list[Incident]:
#     """Мок: возвращает фейковый инцидент для теста.
#     transport должен быть одним из: "bus", "tram", "trolleybus" (на английском)."""
#     # нормализуем русские названия в английские
    
#     transport_norm = normalize_transport(transport)
#     if route == 5 and transport_norm == "tram":
#         return [Incident(
#             id=1, route=5, transport="tram",
#             reason="ДТП на проспекте Ленина",
#             status="active",
#             start_time=datetime.now(),
#             expected_end_time=datetime.now() + timedelta(minutes=20),
#             dispatcher_id="mock"
#         )]
#     return []

# mocks.py — заглушки для разработки ядра
# mocks.py — заглушки для разработки ядра
from contract import Incident, ParsedEvent, TransportType
from datetime import datetime, timedelta

TRANSPORT_MAP = {
    "трамвай": "tram",
    "трамваи": "tram",
    "автобус": "bus",
    "автобусы": "bus",
    "троллейбус": "trolleybus",
    "троллейбусы": "trolleybus",
}

def normalize_transport(transport: str) -> str:
    """Приводит русское/английское название транспорта к каноническому (bus/tram/trolleybus)."""
    if not transport:
        return "bus"  # дефолт, если пусто
    key = transport.strip().lower()
    return TRANSPORT_MAP.get(key, key)  # если не нашли — возвращаем как есть (вдруг уже "tram")


_incidents_store: list[Incident] = [Incident(
            id=1, route=5, transport="tram",
            reason="ДТП на проспекте Ленина",
            status="active",
            start_time=datetime.now(),
            expected_end_time=datetime.now() + timedelta(minutes=20),
            dispatcher_id="mock"
        )]
_next_id = 1


# def mock_get_active_incidents(route: int, transport: str) -> list[Incident]:
#     """Мок: возвращает активные инциденты по конкретному маршруту и типу."""
#     transport_norm = normalize_transport(transport)
#     return [
#         i for i in _incidents_store
#         if i.route == route and i.transport == transport_norm and i.status == "active"
#     ]
def mock_get_active_incidents(route: int, transport: str) -> list[Incident]:
    """Мок: возвращает фейковый инцидент для теста.
    transport должен быть одним из: "bus", "tram", "trolleybus" (на английском)."""
    # нормализуем русские названия в английские
    
    transport_norm = normalize_transport(transport)
    if route == 5 and transport_norm == "tram":
        inc = Incident(
            id=1, route=5, transport="tram",
            reason="ДТП на проспекте Ленина",
            status="active",
            start_time=datetime.now(),
            expected_end_time=datetime.now() + timedelta(minutes=20),
            dispatcher_id="mock"
        )
        return [inc]
    return []


def mock_get_all_active_incidents() -> list[Incident]:
    """Мок: возвращает ВСЕ активные инциденты в городе (без фильтра)."""
    return [i for i in _incidents_store if i.status == "active"]


def mock_confirm_incident(event: ParsedEvent, dispatcher_id: str) -> Incident:
    """Мок: сохраняет инцидент в память и возвращает его с id."""
    global _next_id
    incident = Incident(
        id=_next_id,
        route=event.route,
        transport=event.transport,
        reason=event.reason,
        status="active",
        start_time=datetime.now(),
        expected_end_time=datetime.now() + timedelta(minutes=20),
        dispatcher_id=dispatcher_id,
    )
    _incidents_store.append(incident)
    _next_id += 1
    return incident


def mock_resolve_incident(incident_id: int, dispatcher_id: str) -> Incident | None:
    """Мок: закрывает инцидент по id."""
    for i in _incidents_store:
        if i.id == incident_id:
            i.status = "resolved"
            return i
    return None


def clear_mocks():
    """Очищает хранилище (для тестов)."""
    global _incidents_store, _next_id
    _incidents_store = []
    _next_id = 1