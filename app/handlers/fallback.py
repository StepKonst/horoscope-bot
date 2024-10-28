import logging

from aiogram import Router, types

router = Router()


@router.message()
async def fallback(message: types.Message):
    logging.info(
        f"Неизвестное сообщение от пользователя {message.from_user.id}: {message.text}"
    )
    await message.answer("Извините, я не понял.")
