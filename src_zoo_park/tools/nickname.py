import html
import re
from sqlalchemy import select
from db import User
from sqlalchemy.ext.asyncio import AsyncSession


async def shorten_whitespace_nickname(nickname: str) -> str:
    """Убирает лишние пробелы и делает никнейм однострочным"""
    return re.sub(r"\s+", " ", nickname).strip()


async def has_special_characters_nickname(nickname: str) -> str | None:
    """Возвращает специальные символы, если они есть в никнейме"""
    # Паттерн для поиска специальных символов
    pattern = r"[^a-zA-Zа-яА-Я0-9\-\ ]"
    special_chars = re.findall(pattern, html.unescape(nickname))
    return "".join(special_chars) if special_chars else None


async def is_unique_nickname(session: AsyncSession, nickname: str) -> bool:
    """Проверяет, что никнейм пользователя уникален"""
    users_nickname = await session.scalars(select(User.nickname))
    users_nickname = [
        nickname.lower() for nickname in users_nickname.all() if nickname is not None
    ]
    return nickname.lower() not in users_nickname
