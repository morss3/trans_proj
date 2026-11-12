from mocks import list_subscriptions
from adapters.telegram_adapter import TelegramAdapter
from adapters.vk_adapter import VKAdapter

# Создаем экземпляры для отправки (в реальном проекте их лучше передавать, но для MVP сойдет)
_tg = TelegramAdapter()
_vk = VKAdapter()


async def notify_subscribers(route: int, transport: str, message: str) -> int:
    sent_count = 0
    # В будущем здесь будет запрос к SQLite: "дай всех подписчиков маршрута X"
    # Пока заглушки: мы не можем получить всех пользователей из mocks,
    # так как list_subscriptions требует user_id.
    # Поэтому этот код — заготовка. Когда Человек 4 сделает БД, вы замените его.

    # Псевдокод для будущего:
    # subscribers = db.get_all_subscribers_for_route(route)
    # for sub in subscribers:
    #     if sub.platform == "telegram":
    #         await _tg.send_message(sub.user_id, message)
    #         sent_count += 1
    #     elif sub.platform == "vk":
    #         await _vk.send_message(sub.user_id, message)
    #         sent_count += 1
    return sent_count