#=========================импорты==========================
from aiogram import Router, F
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.types import Message,CallbackQuery
from aiogram.fsm.state import StatesGroup, State
from aiogram.exceptions import TelegramAPIError

from dotenv import load_dotenv
import os

from db import *
from keyboards.keyboards import *

#========================Инициализация======================
load_dotenv()
rt = Router()
admin_user = os.getenv('ADMIN_USERNAME') or 'Владелица студии пока не предоставила своих контактов'
admin_chat = int(os.getenv('ADMIN_CHAT_ID'))
work_time_start = 8
work_time_end = 16 #часы начала и конца рабочего дня студии. Везде стоит -1 т.к. я рассчитываю на то, что последняя запись может быть сделана за час до конца рабочего дня.

#==============Форма для записи================================
class Form(StatesGroup):
    dog_name = State()
    date = State()
    time = State()
#==============Обработчики=====================================
@rt.message(CommandStart()) #команда старт
async def greetings(message: Message,state: FSMContext)->None:
    await message.answer('Приветствую вас в нашей студии выгула собак "Мохнатые друзья"!', reply_markup=start_keyboard())
    await state.clear()

@rt.callback_query(F.data == 'services') #посмотреть услуги
async def services(callback:CallbackQuery)->None:
    await callback.answer()
    full_answer = ''
    services_list = get_services()
    if not services_list:
        await callback.message.answer('Список услуг пока пуст.')
        return
    for service in services_list:
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
    if not message.text: await message.answer(text='пожалуйста, отправьте текстовое сообщение.'); return
    await state.update_data(dog_name = message.text)
    await message.answer("Теперь укажите удобный вам день для выгула", reply_markup = date_keyboard(days_ahead=14,  work_time_start=work_time_start, work_time_end=work_time_end-1))
    await state.set_state(Form.date)

@rt.callback_query(Form.date, F.data.startswith('date:'))
async def sign_up_step3(callback:CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    day = callback.data.split(':',1)[1]
    if not free_hours(day, work_time_start, work_time_end-1):
        await callback.message.edit_text("На эту дату свободного времени уже не осталось. Выберите другой день:",
                                         reply_markup=date_keyboard(14, work_time_start, work_time_end-1))
        await state.set_state(Form.date)
        return
    await state.set_state(Form.time)
    await state.update_data(date = day)
    await callback.message.edit_text("Теперь выберите удобное время:", reply_markup=time_keyboard(work_time_start=work_time_start, work_time_end=work_time_end-1, day= day))

@rt.callback_query(Form.time, F.data.startswith('time:'))
async def sign_up_step4(callback:CallbackQuery, state:FSMContext)->None:
    await callback.answer()
    time = callback.data.split(':')[1]
    await state.update_data(time = time)
    data = await state.get_data()
    saved = insert_order(callback.from_user.full_name, callback.from_user.username or 'нет юзернейма',data['dog_name'], data['date'], data['time'])
    if not saved:
        await callback.message.edit_text('К сожалению, это время уже занято. Начните запись заново: /start')
        await state.clear()
        return
    await callback.message.edit_text(
        f"Ваша запись:\nимя питомца: {data['dog_name']}\nдата: {data['date']}\nвремя: {data['time']}:00")
    try:
        await callback.message.bot.send_message(chat_id=admin_chat,
                                                text = f"Новая запись на выгул!\n"
                                                       f"имя клиента: {callback.from_user.full_name}\n"
                                                       f"Юзернейм клиента: @{callback.from_user.username or 'нет юзернейма'}\n"
                                                       f"имя питомца: {data['dog_name']}\n"
                                                       f"дата: {data['date']}\n"
                                                       f"время: {data['time']}:00")
    except TelegramAPIError as e:
        print('не удалось уведомить владелицу о записи. Пожалуйста, проверьте новые записи в базе данных.')
    await state.clear()
