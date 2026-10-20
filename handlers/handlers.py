#=========================импорты==========================
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from aiogram.fsm.state import StatesGroup, State

import os
from dotenv import load_dotenv
#========================Инициализация======================
load_dotenv()
rt = Router()
admin_user = os.getenv('ADMIN_USERNAME') or '@TestAdmin юзернейм админа не указан, временное решение'
SERVICES = '''Прогулка 30 минут: 400 ₽
Прогулка 60 минут: 700 ₽
Выгул с кормлением: 900 ₽
Передержка (за сутки): 1500 ₽
'''
#==============Форма для записи================================
class Form(StatesGroup):
    dog_name = State()
    time = State()
    date = State()

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
    await state.clear()
