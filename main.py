#=========================импорты==========================
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher
from handlers.admin_handlers import admin_rt
from handlers.main_handlers import rt

from db import init_db
import logging
#========================Инициализация======================
logging.basicConfig(level=logging.INFO)

init_db()
load_dotenv()
TOKEN = os.getenv('TOKEN')
dp = Dispatcher(); dp.include_router(rt); dp.include_router(admin_rt)
#==============Запуск==========================================
async def main()->None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())