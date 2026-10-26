#=========================импорты==========================
from email.mime import message

from aiogram import Router, F
from aiogram.filters import CommandStart, Command
from aiogram.fsm.context import FSMContext
from aiogram.types import Message, InlineKeyboardMarkup, InlineKeyboardButton,CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramAPIError

import os

from aiogram.utils import keyboard
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv
from pydantic.v1.validators import callable_validator

from db import *
from keyboards.keyboards import *

#========================Инициализация======================
load_dotenv()
rt = Router()
admin_user = os.getenv('ADMIN_USERNAME') or 'Владелица студии пока не предоставила своих контактов'
admin_chat = int(os.getenv('ADMIN_CHAT_ID'))
work_time_start = 8
work_time_end = 16 #часы начала и конца рабочего дня студии

#==============Форма для записи================================
class Form(StatesGroup):
    dog_name = State()
    date = State()
    time = State()

class DeleteOrderState(StatesGroup):
    order_id = State()

class ChangeServicesState(StatesGroup):
    delete_service_id = State()
    service_id = State()
    service_name = State()
    service_price = State()
    add_service_name = State()
    add_service_price = State()
#==============Обработчики=====================================
@rt.message(CommandStart()) #команда старт
async def greetings(message: Message,state: FSMContext)->None:
    print(message.chat.id)
    await message.answer('Приветствую вас в нашей студии выгула собак "Мохнатые друзья"!', reply_markup=start_keyboard())
    await state.clear()

@rt.callback_query(F.data == 'services') #посмотреть услуги
async def services(callback:CallbackQuery)->None:
    await callback.answer()
    full_answer = ''
    for service in get_services():
        full_answer +=f'{service[1]} - {service[2]} рублей\n'
    await callback.message.answer(full_answer)

@rt.callback_query(F.data == 'contact') #связаться с владелицей
async def contact(callback:CallbackQuery)->None:
    await callback.answer()
    await callback.message.answer(f'Вот юзернейм владелицы студии: {admin_user}')

#===================================Запись на выгул=============================================
@rt.callback_query(F.data == 'sign_up')
async def sign_up_step1(callback:CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    await callback.message.answer("Как зовут вашего питомца?")
    await state.set_state(Form.dog_name)

@rt.message(Form.dog_name)
async def sign_up_step2(message: Message, state:FSMContext)->None:
    await state.update_data(dog_name = message.text)
    await message.answer("Теперь укажите удобный вам день для выгула", reply_markup = date_keyboard(days_ahead=14))
    await state.set_state(Form.date)

@rt.callback_query(Form.date, F.data.startswith('date:'))
async def sign_up_step3(callback:CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    day = callback.data.split(':',1)[1]
    await state.set_state(Form.time)
    await state.update_data(date = day)

    await callback.message.edit_text("Теперь выберите удобное время:", reply_markup=time_keyboard(work_time_start=work_time_start, work_time_end=work_time_end, day= day))

@rt.callback_query(Form.time, F.data.startswith('time:'))
async def sign_up_step4(callback:CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    time = callback.data.split(':')[1]
    await state.update_data(time = time)
    data = await state.get_data()
    await callback.message.edit_text(f"Ваша запись:\nимя питомца: {data['dog_name']}\nдата: {data['date']}\nвремя: {data['time']}")
    insert_order(callback.from_user.full_name,callback.from_user.username, data['dog_name'], data['date'], data['time'])
    try:
        await callback.message.bot.send_message(chat_id=admin_chat,
                                                text = f"Новая запись на выгул!\n"
                                                       f"имя клиента: {callback.from_user.full_name}\n"
                                                       f"Юзернейм клиента: @{callback.from_user.username}\n"
                                                       f"имя питомца: {data['dog_name']}\n"
                                                       f"дата: {data['date']}\n"
                                                       f"время: {data['time']}")
    except TelegramAPIError as e:
        await callback.message.answer("Не удалось уведомить владелицу о вашей записи. Попробуйте позже\n");print(e)
    await state.clear()

#========================================Панель администратора===========================================================================
@rt.message(Command('admin'))
async def admin_menu (message: Message,state: FSMContext)->None:
    if f"@{message.from_user.username}" == admin_user:
        await message.answer(text = 'Приветствуем вас в настройках администратора! Здесь вы можете настроить данного бота.', reply_markup=admin_keyboard())
        await state.clear()

#=====================================Кнопки администратора=================================================================================

@rt.callback_query(F.data == 'orders')
async def orders_menu (callback: CallbackQuery,state:FSMContext)->None:
    await callback.answer()
    if f"@{callback.from_user.username}" != admin_user:
        return
    orders = get_orders()
    await callback.message.answer(text=orders or 'записей пока нет', reply_markup=orders_keyboard() if orders else None)
    await state.clear()

@rt.callback_query(F.data == 'delete_order')
async def select_order_for_delete (callback: CallbackQuery,state:FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text='Укажите номер записи, которую необходимо удалить')
    await state.clear()
    await state.set_state(DeleteOrderState.order_id)

@rt.message(DeleteOrderState.order_id)
async def delete_selected_order (message:Message,state:FSMContext)->None:
    delete_order(int(message.text))
    await message.answer(text=f'Запись номер {message.text} удалена!')
    await state.clear()

#===============================Меню изменения услуг==================================
@rt.callback_query(F.data == 'change_services')
async def change_services_menu (callback: CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    full_text = 'Вот текущий список услуг:\n'
    for service in get_services():
        full_text+=f'''услуга номер {service[0]}:
наименование: {service[1]}
цена: {service[2]}

'''
    await callback.message.answer(text = full_text, reply_markup=services_keyboard())
    await state.clear()
#==================================удаление услуги====================================
@rt.callback_query(F.data == 'remove_service')
async def remove_service (callback: CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    await state.clear()
    await callback.message.answer(text = 'укажите номер услуги, которую необходимо удалить')
    await state.set_state(ChangeServicesState.delete_service_id)

@rt.message(ChangeServicesState.delete_service_id)
async def delete_selected_service (message: Message,state: FSMContext)->None:
    delete_service(int(message.text))
    await message.answer(text = 'услуга успешно удалена')
    await state.clear()

#==============================Изменение услуги=========================================

@rt.callback_query(F.data == 'change_service')
async def select_change_service (callback: CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text='укажите номер услуги, которую необходимо изменить')
    await state.clear()
    await state.set_state(ChangeServicesState.service_id)

@rt.message(ChangeServicesState.service_id)
async def change_selected_service_step1 (message: Message,state: FSMContext)->None:
    await message.answer(text='Укажите новое имя услуги.')
    await state.update_data(service_id=int(message.text))
    await state.set_state(ChangeServicesState.service_name)

@rt.message(ChangeServicesState.service_name)
async def change_selected_service_step2 (message: Message,state: FSMContext)->None:
    await message.answer(text='укажите новую цену услуги')
    await state.update_data(service_name=message.text)
    await state.set_state(ChangeServicesState.service_price)

@rt.message(ChangeServicesState.service_price)
async def change_selected_service_step3 (message: Message,state: FSMContext)->None:
    await message.answer(text='Услуга успешно изменена')
    await state.update_data(service_price=int(message.text))
    data = await state.get_data()
    change_service(data['service_id'],data['service_name'],data['service_price'])
    await state.clear()

#====================================Добавление услуги===================================

@rt.callback_query(F.data == 'add_service')
async def add_service_step1 (callback: CallbackQuery, state: FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text = 'Укажите имя новой услуги')
    await state.clear()
    await state.set_state(ChangeServicesState.add_service_name)

@rt.message(ChangeServicesState.add_service_name)
async def add_service_step2 (message: Message,state: FSMContext)->None:
    await message.answer(text='Укажите цену услуги')
    await state.set_state(ChangeServicesState.add_service_price)
    await state.update_data(add_service_name=message.text)

@rt.message(ChangeServicesState.add_service_price)
async def add_service_step3 (message: Message,state: FSMContext)->None:
    await state.update_data(add_service_price=int(message.text))
    data = await state.get_data()
    add_service(data['add_service_name'],data['add_service_price'])
    await message.answer(text = f'Новая услуга добавлена:\n{data["add_service_name"]} - {data["add_service_price"]} рублей')
    await state.clear()
