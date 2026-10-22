#=========================импорты==========================
from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramAPIError

import os

from aiogram.utils import keyboard
from dotenv import load_dotenv

from db import *
#========================Инициализация======================
load_dotenv()
rt = Router()
admin_user = os.getenv('ADMIN_USERNAME') or 'Владелица студии пока не предоставила своих контактов'
admin_chat = int(os.getenv('ADMIN_CHAT_ID'))
SERVICES = '''Прогулка 30 минут: 400 ₽
Прогулка 60 минут: 700 ₽
Выгул с кормлением: 900 ₽
Передержка (за сутки): 1500 ₽
'''
#==============Форма для записи================================
class Form(StatesGroup):
    dog_name = State()
    date = State()
    time = State()


#==============Обработчики=====================================
@rt.message(CommandStart())
async def greetings(message: Message,state: FSMContext)->None:
#   ============кнопки===============
    button1 = InlineKeyboardButton(text = 'Услуги и цены',callback_data = 'services')
    button2 = InlineKeyboardButton(text = 'Связаться с владелицей',callback_data = 'contact')
    button3 = InlineKeyboardButton(text = 'Записаться на выгул',callback_data = 'sign_up')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1, button2],[button3]])
#   =============Ответ================
    await message.answer('Приветствую вас в нашей студии выгула собак "Мохнатые друзья"!',reply_markup=keyboard)
    await state.clear()

#========================================Панель администратора===========================================================================
@rt.message(Command('admin'))
async def admin_menu (message: Message,state: FSMContext)->None:
    if message.from_user.username == admin_user:
        button1 = InlineKeyboardButton (text = 'Посмотреть записи',callback_data = 'orders')
        button2 = InlineKeyboardButton (text = 'Изменить услуги', callback_data = 'change_services')
        keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1],[ button2]])
        await message.answer(text = 'Приветствуем вас в настройках администратора! Здесь вы можете настроить данного бота.', reply_markup=keyboard)
        await state.clear()

#=====================================Кнопки администратора=================================================================================

@rt.callback_query(Command('orders'))
async def orders_menu (message: Message,state: FSMContext)->None:
    orders = get_orders()
    final_answer = ''
    for order in orders:
        final_answer += order + '\n'
    await message.answer(text=final_answer, reply_markup=keyboard)

@rt.callback_query(F.data == 'services')
async def services(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer(SERVICES)

@rt.callback_query(F.data == 'contact')
async def contact(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer(f'Вот юзернейм владелицы студии: {admin_user}')

@rt.callback_query(F.data == 'sign_up')
async def sign_up_step1(callback:CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    await callback.message.answer("Как зовут вашего питомца?")
    await state.set_state(Form.dog_name)

@rt.message(Form.dog_name)
async def sign_up_step2(message: Message, state:FSMContext)->None:
    await state.update_data(dog_name = message.text)
    await message.answer("Теперь укажите удобный вам день для выгула")
    await state.set_state(Form.date)

@rt.message(Form.date)
async def sign_up_step3(message: Message, state:FSMContext)->None:
    await state.update_data(date = message.text)
    await state.set_state(Form.time)
    await message.answer("Теперь укажите удобное вам время")

@rt.message(Form.time)
async def sign_up_step4(message: Message, state:FSMContext)->None:
    await state.update_data(time = message.text)
    data = await state.get_data()
    await message.answer(f"Ваша запись:\nимя питомца: {data['dog_name']}\nдата: {data['date']}\nвремя: {data['time']}")
    try:
        await message.bot.send_message(chat_id=admin_chat,text = f"Новая запись на выгул!\nимя клиента: {message.from_user.full_name}\nимя питомца: {data['dog_name']}\nдата: {data['date']}\nвремя: {data['time']}")
    except TelegramAPIError as e:
        await message.answer("Не удалось уведомить владелицу о вашей записи. Попробуйте позже\n");print(e)
    await state.clear()
