import asyncio, os
from dotenv import load_dotenv
from adapters.telegram_adapter import TelegramAdapter
load_dotenv()
async def run():
    bot = TelegramAdapter()
    await bot.start_polling()
if __name__ == "__main__":
    asyncio.run(run())