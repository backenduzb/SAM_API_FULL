from aiogram import Bot, Dispatcher, F
from aiogram.filters import Command
from aiogram.types import Message
from aiogram.utils.keyboard import ReplyKeyboardBuilder
from aiogram.fsm.storage.memory import MemoryStorage
import asyncio
import logging

logging.basicConfig(level=logging.INFO)

from data.config import BOT_TOKEN
from handlers import start  

async def main():
    bot = Bot(token=BOT_TOKEN)
    dp = Dispatcher(storage=MemoryStorage())

    dp.include_router(start.router)

    print("Bot ishga tushdi!")
    await dp.start_polling(bot)

if __name__ == "__main__":
    asyncio.run(main())


# import requests

# # API endpoint
# edited_url = "http://localhost:8000/api/teacher-users-stats/80/"

# # To'g'rilangan ma'lumotlar
# data = {
#     "umuman_qoniqaman": 1  # Field nomini to'g'riladim
# }

# # PUT so'rovini yuborish
# response = requests.put(edited_url, json=data)