import os
from aiogram import Bot, Dispatcher
from aiogram.filters import Command
from aiogram.types import Message
from trans_proj.agent import agent
from trans_proj.mocks import add_subscription, remove_subscription, list_subscriptions

class TelegramAdapter:
    def __init__(self):
        # Берем имя переменной из .env.example
        self.bot = Bot(token=os.getenv("TELEGRAM_BOT_KEY"))
        self.dp = Dispatcher()
        self._register()

    def _register(self):
        @self.dp.message(Command("start"))
        async def start(m: Message):
            await m.answer("Привет! Напиши вопрос или /subscribe 5")

        @self.dp.message(Command("subscribe"))
        async def sub(m: Message):
            args = m.text.split()
            if len(args) < 2 or not args[1].isdigit():
                return await m.answer("Формат: /subscribe 5")
            ok = add_subscription(str(m.from_user.id), "telegram", int(args[1]), "bus")
            await m.answer("Добавлено ✅" if ok else "Уже подписаны")

        @self.dp.message()
        async def text(m: Message):
            # Вызываем агента так же, как в agent.py
            result = agent.invoke({"messages": [("user", m.text)]})
            answer = result["messages"][-1].content
            await m.answer(answer)

    async def send_message(self, user_id: str, text: str) -> None:
        await self.bot.send_message(chat_id=int(user_id), text=text)

    async def start_polling(self) -> None:
        await self.dp.start_polling(self.bot)