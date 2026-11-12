import asyncio
from dotenv import load_dotenv
from adapters.telegram_adapter import TelegramAdapter
from adapters.vk_adapter import VKAdapter

load_dotenv()

async def main():
    tg = TelegramAdapter()
    vk = VKAdapter()
    # Запускаем оба бота одновременно
    await asyncio.gather(tg.start_polling(), vk.start_polling())

if __name__ == "__main__":
    asyncio.run(main())