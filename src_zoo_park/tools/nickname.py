import html
import re
from sqlalchemy import select
from init_db import _sessionmaker_for_func
from db import User


async def shorten_whitespace_nickname(nickname: str) -> str:
    """Убирает лишние пробелы и делает никнейм однострочным"""
    return re.sub(r"\s+", " ", nickname).strip()


async def has_special_characters_nickname(nickname: str) -> str | None:
    """Возвращает специальные символы, если они есть в никнейме"""
    # Паттерн для поиска специальных символов
    pattern = r"[^a-zA-Zа-яА-Я0-9\-\ ]"
    special_chars = re.findall(pattern, html.unescape(nickname))
    return "".join(special_chars) if special_chars else None


async def is_unique_nickname(nickname: str) -> bool:
    """Проверяет, что никнейм пользователя уникален"""
    async with _sessionmaker_for_func() as session:
        users_nickname = await session.scalars(select(User.nickname))
        users_nickname = [
            nickname.lower()
            for nickname in users_nickname.all()
            if nickname is not None
        ]
        if nickname.lower() in users_nickname:
            return False
    return True
