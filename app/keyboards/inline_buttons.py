from aiogram import types


def get_update_button():
    button = types.InlineKeyboardButton(
        text="Обновить", callback_data="update_horoscope"
    )
    return types.InlineKeyboardMarkup(inline_keyboard=[[button]])
