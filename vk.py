import asyncio
import os
from dotenv import load_dotenv
from adapters.vk_adapter import VKAdapter

load_dotenv()

async def run():
    bot = VKAdapter()
    await bot.start_polling()

if __name__ == "__main__":
    asyncio.run(run())