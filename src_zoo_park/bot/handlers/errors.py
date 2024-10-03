from aiogram import Router
from aiogram.types import ErrorEvent

router = Router()


@router.error()
async def error_handler(event: ErrorEvent):
    print(event.exception)
