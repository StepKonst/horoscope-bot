from datetime import date

from aiogram import F, Router, types
from aiogram.enums import ParseMode
from aiogram.filters import CommandStart
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import State, StatesGroup

import app.keyboards.zodiac_keyboard as kb
from app.constants import ZODIAC_SIGNS, generate_horoscope_message
from app.database.requests import set_user_zodiac
from app.keyboards.inline_buttons import get_update_button

router = Router()


class RegistrationState(StatesGroup):
    choosing_zodiac = State()


@router.message(CommandStart())
async def cmd_start(message: types.Message, state: FSMContext):
    await state.set_state(RegistrationState.choosing_zodiac)
    await message.answer(
        "Привет! Выбери свой знак зодиака:", reply_markup=kb.get_zodiac_kb()
    )


@router.message(RegistrationState.choosing_zodiac, F.text.in_(ZODIAC_SIGNS))
async def zodiac_choice_handler(message: types.Message, state: FSMContext):
    chosen_zodiac = message.text
    description = ZODIAC_SIGNS.get(chosen_zodiac, "Информация о знаке отсутствует.")

    horoscope_text = generate_horoscope_message()

    await set_user_zodiac(
        telegram_id=message.from_user.id,
        zodiac_sign=chosen_zodiac,
        last_horoscope_text=horoscope_text,
        last_horoscope_date=date.today(),
        zodiac_message_id=message.message_id,
    )

    await message.answer(
        f"Вы выбрали {chosen_zodiac}.\n\n{description}\n\nТеперь я буду отправлять вам гороскоп.",
        reply_markup=types.ReplyKeyboardRemove(),
    )

    await state.clear()

    await message.answer_photo(
        photo="https://www.pravmir.ru/wp-content/uploads/2015/08/Goroskop-768x480.jpg",
        caption=horoscope_text,
        reply_markup=get_update_button(),
        parse_mode=ParseMode.HTML,
    )
