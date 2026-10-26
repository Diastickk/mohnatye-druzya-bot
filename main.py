#=========================импорты==========================
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from handlers.handlers import rt

from db import init_db
#========================Инициализация======================
init_db()
load_dotenv()
TOKEN = os.getenv('TOKEN')
dp = Dispatcher(); dp.include_router(rt)
#==============Запуск==========================================
async def main()->None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())