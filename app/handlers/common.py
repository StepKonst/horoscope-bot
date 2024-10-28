from datetime import datetime

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.exceptions import TelegramBadRequest
from aiogram.filters import Command

from app.constants import ZODIAC_SIGNS, generate_horoscope_message
from app.database.requests import get_user, set_user_zodiac
from app.keyboards.inline_buttons import get_update_button
from app.keyboards.zodiac_keyboard import get_zodiac_kb

router = Router()


async def send_horoscope_message(message: types.Message, text: str) -> int:
    msg = await message.answer_photo(
        photo="https://www.pravmir.ru/wp-content/uploads/2015/08/Goroskop-768x480.jpg",
        caption=text,
        reply_markup=get_update_button(),
        parse_mode=ParseMode.HTML,
    )
    return msg.message_id


@router.message(Command("change_zodiac"))
async def change_zodiac(message: types.Message):
    await message.answer("Выберите новый знак зодиака:", reply_markup=get_zodiac_kb())


@router.message(Command("clear_history"))
async def clear_history(message: types.Message):
    user = await get_user(message.from_user.id)
    if user:
        last_message_id = user.zodiac_message_id
        try:
            for i in range(message.message_id, 0, -1):
                if i != last_message_id:
                    await message.bot.delete_message(message.from_user.id, i)

            await message.answer(
                "История сообщений очищена, оставлено последнее сообщение с вашим знаком зодиака."
            )
        except TelegramBadRequest as ex:
            if ex.message == "Bad Request: message to delete not found":
                print("Некоторые сообщения уже удалены или не найдены.")
            else:
                print(f"Ошибка при удалении сообщения: {ex}")
    else:
        await message.answer("Не удалось найти вашу информацию.")


@router.message(F.text.in_(ZODIAC_SIGNS))
async def zodiac_choice_handler(message: types.Message):
    chosen_zodiac = message.text
    today = datetime.now().date()

    horoscope_text = generate_horoscope_message()

    await set_user_zodiac(
        telegram_id=message.from_user.id,
        zodiac_sign=chosen_zodiac,
        last_horoscope_text=horoscope_text,
        last_horoscope_date=today,
        zodiac_message_id=message.message_id,
    )

    await message.answer(
        f"Вы выбрали {chosen_zodiac}.\n\nТеперь ваш знак зодиака изменен.",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    await send_horoscope_message(message, horoscope_text)
