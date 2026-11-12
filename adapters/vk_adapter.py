import os
from vkbottle.bot import Bot, Message
from trans_proj.agent import agent
from trans_proj.mocks import add_subscription, remove_subscription, list_subscriptions

class VKAdapter:
    def __init__(self):
        self.bot = Bot(token=os.getenv("VK_TOKEN"))

        @self.bot.on.message(text="/start")
        async def start(m: Message):
            await m.answer("Привет! Напиши вопрос или /subscribe 5")

        @self.bot.on.message(text="/subscribe <route:int>")
        async def sub(m: Message, route: int):
            ok = add_subscription(str(m.from_id), "vk", route, "bus")
            await m.answer("Добавлено" if ok else "Уже подписаны")

        @self.bot.on.message()
        async def text(m: Message):
            result = agent.invoke({"messages": [("user", m.text)]})
            await m.answer(result["messages"][-1].content)

    async def send_message(self, user_id: str, text: str) -> None:
        await self.bot.api.messages.send(user_id=int(user_id), message=text, random_id=0)

    async def start_polling(self) -> None:
        await self.bot.run_polling()