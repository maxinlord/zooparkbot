from aiogram.types import ErrorEvent
from aiogram import Router



router = Router()

@router.error()
async def error_handler(event: ErrorEvent):
    print(event.exception)