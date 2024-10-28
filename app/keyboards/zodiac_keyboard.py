from aiogram import types
from aiogram.utils.keyboard import ReplyKeyboardBuilder

from app.constants import ZODIAC_SIGNS


def get_zodiac_kb() -> types.ReplyKeyboardMarkup:
    builder = ReplyKeyboardBuilder()

    for sign in ZODIAC_SIGNS:
        builder.button(text=sign)
    builder.adjust(4)

    return builder.as_markup(one_time_keyboard=True, resize_keyboard=True)
