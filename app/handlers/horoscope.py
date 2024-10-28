from datetime import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import Command

from app.constants import generate_horoscope_message
from app.database.requests import get_user, update_user_horoscope
from app.keyboards.inline_buttons import get_update_button

router = Router()


async def send_horoscope_message(message: types.Message, text: str) -> int:
    await message.reply_photo(
        photo="https://www.pravmir.ru/wp-content/uploads/2015/08/Goroskop-768x480.jpg",
        caption=text,
        reply_markup=get_update_button(),
        parse_mode=ParseMode.HTML,
    )


@router.message(Command("update"))
async def update_horoscope_command(message: types.Message):
    today = datetime.now().date()
    user = await get_user(message.from_user.id)

    if user and user.last_horoscope_date == today:
        updated_text = generate_horoscope_message()
        await send_horoscope_message(message, updated_text)
        await update_user_horoscope(message.from_user.id, today, updated_text)
    else:
        horoscope_text = generate_horoscope_message(user.zodiac_sign)
        await send_horoscope_message(message, horoscope_text)
        await update_user_horoscope(message.from_user.id, today, horoscope_text)


@router.callback_query(F.data == "update_horoscope")
async def update_horoscope_callback(callback_query: types.CallbackQuery):
    updated_text = generate_horoscope_message()
    await callback_query.message.edit_caption(
        caption=updated_text,
        reply_markup=get_update_button(),
        parse_mode=ParseMode.HTML,
    )
    await update_user_horoscope(
        callback_query.from_user.id,
        datetime.now().date(),
        updated_text,
        update_zodiac_message_id=False,
    )
    await callback_query.answer("Прогноз обновлен!")
