import asyncio
import logging
import sys
from datetime import datetime

from aiogram import Bot, Dispatcher
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from apscheduler.schedulers.asyncio import AsyncIOScheduler

from app.constants import TELEGRAM_TOKEN, generate_horoscope_message
from app.database.models import init_db
from app.database.requests import get_all_users, update_user_horoscope
from app.handlers import common, fallback, horoscope, registration
from app.keyboards.inline_buttons import get_update_button

dp = Dispatcher()
bot = Bot(token=TELEGRAM_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML))
scheduler = AsyncIOScheduler()


async def set_commands(bot: Bot):
    commands = [
        BotCommand(command="/start", description="Запустить бота"),
        BotCommand(command="/update", description="Обновить прогноз"),
        BotCommand(command="/change_zodiac", description="Сменить знак зодиака"),
        BotCommand(command="/clear_history", description="Очистить историю"),
    ]
    await bot.set_my_commands(commands)


async def send_daily_horoscope():
    users = await get_all_users()
    today = datetime.now().date()

    for user in users:
        # if user.last_horoscope_date != today:
        horoscope_text = generate_horoscope_message()
        await bot.send_photo(
            chat_id=user.telegram_id,
            photo="https://www.pravmir.ru/wp-content/uploads/2015/08/Goroskop-768x480.jpg",
            caption=horoscope_text,
            reply_markup=get_update_button(),
            parse_mode=ParseMode.HTML,
        )
        await update_user_horoscope(user.telegram_id, today, horoscope_text)


async def main() -> None:
    await init_db()
    await set_commands(bot)

    dp.include_router(registration.router)
    dp.include_router(horoscope.router)
    dp.include_router(common.router)
    dp.include_router(fallback.router)

    scheduler.add_job(send_daily_horoscope, "cron", hour=10, minute=0)
    scheduler.start()

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot)


if __name__ == "__main__":
    logging.basicConfig(
        level=logging.INFO,
        format=(
            "%(asctime)s -- %(levelname)s: def %(funcName)s in line #"
            '%(lineno)d, logging message -- "%(message)s" || %(name)s'
        ),
        stream=sys.stdout,
    )
    asyncio.run(main())
