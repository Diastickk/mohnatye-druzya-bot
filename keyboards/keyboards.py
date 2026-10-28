from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton

from datetime import date, timedelta
from db import *

def start_keyboard():
    button1 = InlineKeyboardButton(text='Услуги и цены', callback_data='services')
    button2 = InlineKeyboardButton(text='Связаться с владелицей', callback_data='contact')
    button3 = InlineKeyboardButton(text='Записаться на выгул', callback_data='sign_up')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1],[button2], [button3]])
    return keyboard

def free_hours(day: str, work_time_start: int, work_time_end: int) -> list[int]:
    busy = set(get_ordered_time(day))
    return [h for h in range(work_time_start, work_time_end + 1) if h not in busy]

def date_keyboard(days_ahead: int = 14, work_time_start: int = 8, work_time_end: int = 16):
    builder = InlineKeyboardBuilder()
    today = date.today()
    for i in range(1, days_ahead + 1):
        d = today + timedelta(days=i)
        if d.weekday() == 6:
            continue
        if not free_hours(d.isoformat(), work_time_start, work_time_end):
            continue
        builder.button(text=d.strftime('%d.%m'), callback_data=f"date:{d.isoformat()}")
    builder.adjust(4)
    return builder.as_markup()

def time_keyboard(work_time_start, work_time_end, day):
    builder = InlineKeyboardBuilder()
    for hour in free_hours(day, work_time_start, work_time_end):
        builder.button(text=f"{hour}:00", callback_data=f"time:{hour}")
    builder.adjust(3)
    return builder.as_markup()

def admin_keyboard():
    button1 = InlineKeyboardButton(text='Посмотреть записи', callback_data='orders')
    button2 = InlineKeyboardButton(text='Изменить услуги', callback_data='change_services')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2]])
    return keyboard

def orders_keyboard():
    button = InlineKeyboardButton(text = 'Удалить запись', callback_data = 'delete_order')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button]])
    return keyboard

def services_keyboard():
    button1 = InlineKeyboardButton(text = 'удалить услугу',callback_data = 'remove_service')
    button2 = InlineKeyboardButton(text= 'изменить услугу',callback_data = 'change_service')
    button3 = InlineKeyboardButton(text='добавить услугу',callback_data = 'add_service')
    keyboard = InlineKeyboardMarkup(inline_keyboard=[[button1], [button2],[button3]])
    return keyboard