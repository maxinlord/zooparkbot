from sqlalchemy import select
from aiogram.types import Message, InputFile
from db import Photo
from cache import photo_cache
from sqlalchemy.ext.asyncio import AsyncSession


async def get_photo(session: AsyncSession, photo_name: str):
    if photo_name in photo_cache:
        return photo_cache[photo_name]
    return await session.scalar(select(Photo.photo_id).where(Photo.name == photo_name))


async def get_photo_from_message(message: Message) -> str:
    return message.photo[-1].file_id if message.photo else None
