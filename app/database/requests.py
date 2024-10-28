from datetime import date

from sqlalchemy import select, update

from app.database.models import User, async_session


async def set_user_zodiac(
    telegram_id: int,
    zodiac_sign: str,
    last_horoscope_text: str,
    last_horoscope_date: date,
    zodiac_message_id: int,
) -> None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))

        if not user:
            user = User(
                telegram_id=telegram_id,
                zodiac_sign=zodiac_sign,
                last_horoscope_text=last_horoscope_text,
                last_horoscope_date=last_horoscope_date,
                zodiac_message_id=zodiac_message_id,
            )
            session.add(user)
        else:
            user.zodiac_sign = zodiac_sign
            user.last_horoscope_text = last_horoscope_text
            user.last_horoscope_date = last_horoscope_date
            user.zodiac_message_id = zodiac_message_id

        await session.commit()


async def get_all_users() -> list[User]:
    async with async_session() as session:
        result = await session.execute(select(User))
        return result.scalars().all()


async def update_user_horoscope(
    telegram_id: int,
    horoscope_date: date,
    horoscope_text: str,
    zodiac_message_id: int = None,
    update_zodiac_message_id: bool = True,
) -> None:
    async with async_session() as session:
        values = {
            "last_horoscope_date": horoscope_date,
            "last_horoscope_text": horoscope_text,
        }

        if update_zodiac_message_id and zodiac_message_id is not None:
            values["zodiac_message_id"] = zodiac_message_id

        await session.execute(
            update(User).where(User.telegram_id == telegram_id).values(**values)
        )
        await session.commit()


async def get_user(telegram_id: int) -> User | None:
    async with async_session() as session:
        user = await session.scalar(select(User).where(User.telegram_id == telegram_id))
        return user
