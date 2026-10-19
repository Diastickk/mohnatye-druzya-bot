#=========================импорты==========================
import asyncio
import os
from dotenv import load_dotenv

from aiogram import Bot, Dispatcher, F
from aiogram.filters import CommandStart
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery

#========================Инициализация======================
load_dotenv()
TOKEN = os.getenv('TOKEN'); dp = Dispatcher()
admin_user = os.getenv('ADMIN_USERNAME') or '@TestAdmin юзернейм админа не указан, временное решение'
SERVICES = '''Прогулка 30 минут: 400 ₽
Прогулка 60 минут: 700 ₽
Выгул с кормлением: 900 ₽
Передержка (за сутки): 1500 ₽
'''
#=======================основная логика======================
@dp.message(CommandStart())
async def greetings(message: Message)->None:
#   ============кнопки===============
    button1 = InlineKeyboardButton(text = 'Услуги и цены',callback_data = 'services')
    button2 = InlineKeyboardButton(text = 'Связаться с владелицей',callback_data = 'contact')
    button3 = InlineKeyboardButton(text = 'Записаться на выгул',callback_data = 'sign_up')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2],[button3]])
#   =============Ответ================
    await message.answer('Приветствую вас в нашей студии выгула собак "Мохнатые друзья"!',reply_markup=keyboard)
#==============Обработчики=====================================
@dp.callback_query(F.data == 'services')
async def services(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer(SERVICES)

@dp.callback_query(F.data == 'contact')
async def contact(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer(f'Вот юзернейм владелицы студии: {admin_user}')

@dp.callback_query(F.data == 'sign_up')
async def sign_up(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer('Функция в разработке')
#==============Запуск==========================================
async def main()->None:
    bot = Bot(token=TOKEN)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())