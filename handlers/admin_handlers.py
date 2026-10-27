from aiogram import Router, F
from aiogram.filters import BaseFilter, Command
from aiogram.types import Message, CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.fsm.context import FSMContext

import os
from dotenv import load_dotenv
from db import *
from keyboards.keyboards import *

load_dotenv()
ADMIN_ID = int(os.getenv('ADMIN_ID'))

class IsAdmin(BaseFilter):
    async def __call__(self, event: Message | CallbackQuery) -> bool:
        return event.from_user.id == ADMIN_ID

admin_rt = Router()
admin_rt.message.filter(IsAdmin())
admin_rt.callback_query.filter(IsAdmin())

class DeleteOrderState(StatesGroup):
    order_id = State()

class ChangeServicesState(StatesGroup):
    delete_service_id = State()
    service_id = State()
    service_name = State()
    service_price = State()
    add_service_name = State()
    add_service_price = State()

#========================================Панель администратора===========================================================================
@admin_rt.message(Command('admin'))
async def admin_menu (message: Message,state:FSMContext)->None:
    await message.answer(text = 'Приветствуем вас в настройках администратора! Здесь вы можете настроить данного бота.', reply_markup=admin_keyboard())
    await state.clear()

#=====================================Кнопки администратора=================================================================================

@admin_rt.callback_query(F.data == 'orders')
async def orders_menu (callback: CallbackQuery,state:FSMContext)->None:
    await callback.answer()
    orders = get_orders()
    await callback.message.answer(text=orders or 'записей пока нет', reply_markup=orders_keyboard() if orders else None)
    await state.clear()

@admin_rt.callback_query(F.data == 'delete_order')
async def select_order_for_delete (callback: CallbackQuery,state:FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text='Укажите номер записи, которую необходимо удалить')
    await state.clear()
    await state.set_state(DeleteOrderState.order_id)

@admin_rt.message(DeleteOrderState.order_id)
async def delete_selected_order (message:Message,state:FSMContext)->None:
    try:
        delete_order(int(message.text))
    except:
        await message.answer(text='Пожалуйста, введите число')
        return
    await message.answer(text=f'Запись номер {message.text} удалена!')
    await state.clear()

#===============================Меню изменения услуг==================================
@admin_rt.callback_query(F.data == 'change_services')
async def change_services_menu (callback: CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    full_text = 'Вот текущий список услуг:\n'
    services_list = get_services()
    if not services_list:
        await callback.message.answer('Список услуг пока пуст.', reply_markup=services_keyboard())
        return
    for service in services_list:
        full_text+=f'''услуга номер {service[0]}:
наименование: {service[1]}
цена: {service[2]}

'''
    await callback.message.answer(text = full_text, reply_markup=services_keyboard())
    await state.clear()
#==================================удаление услуги====================================
@admin_rt.callback_query(F.data == 'remove_service')
async def remove_service (callback: CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    await state.clear()
    await callback.message.answer(text = 'укажите номер услуги, которую необходимо удалить')
    await state.set_state(ChangeServicesState.delete_service_id)

@admin_rt.message(ChangeServicesState.delete_service_id)
async def delete_selected_service (message: Message,state:FSMContext)->None:
    try:
        delete_service(int(message.text))
    except:
        await message.answer(text='Пожалуйста, введите число')
        return
    await message.answer(text = 'услуга успешно удалена')
    await state.clear()

#==============================Изменение услуги=========================================

@admin_rt.callback_query(F.data == 'change_service')
async def select_change_service (callback: CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text='укажите номер услуги, которую необходимо изменить')
    await state.clear()
    await state.set_state(ChangeServicesState.service_id)

@admin_rt.message(ChangeServicesState.service_id)
async def change_selected_service_step1 (message: Message,state:FSMContext)->None:
    await message.answer(text='Укажите новое имя услуги.')
    try:
        await state.update_data(service_id=int(message.text))
    except:
        await message.answer(text='Пожалуйста, введите число')
        return
    await state.set_state(ChangeServicesState.service_name)

@admin_rt.message(ChangeServicesState.service_name)
async def change_selected_service_step2 (message: Message,state:FSMContext)->None:
    await message.answer(text='укажите новую цену услуги')
    await state.update_data(service_name=message.text)
    await state.set_state(ChangeServicesState.service_price)

@admin_rt.message(ChangeServicesState.service_price)
async def change_selected_service_step3 (message: Message,state:FSMContext)->None:
    try:
        await state.update_data(service_price=int(message.text))
    except:
        await message.answer(text='Пожалуйста, введите число')
        return
    data = await state.get_data()
    change_service(data['service_id'],data['service_name'],data['service_price'])
    await state.clear()
    await message.answer(text='Услуга успешно изменена')

#====================================Добавление услуги===================================

@admin_rt.callback_query(F.data == 'add_service')
async def add_service_step1 (callback: CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    await callback.message.answer(text = 'Укажите имя новой услуги')
    await state.clear()
    await state.set_state(ChangeServicesState.add_service_name)

@admin_rt.message(ChangeServicesState.add_service_name)
async def add_service_step2 (message: Message,state:FSMContext)->None:
    await message.answer(text='Укажите цену услуги')
    await state.set_state(ChangeServicesState.add_service_price)
    await state.update_data(add_service_name=message.text)

@admin_rt.message(ChangeServicesState.add_service_price)
async def add_service_step3 (message: Message,state:FSMContext)->None:
    try:
        await state.update_data(add_service_price=int(message.text))
    except:
        await message.answer(text='Пожалуйства введите число')
        return
    data = await state.get_data()
    add_service(data['add_service_name'],data['add_service_price'])
    await message.answer(text = f'Новая услуга добавлена:\n{data["add_service_name"]} - {data["add_service_price"]} рублей')
    await state.clear()
