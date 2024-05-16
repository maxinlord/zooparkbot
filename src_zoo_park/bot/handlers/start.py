from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import default_state


router = Router()


@router.message(CommandStart(deep_link=True))
async def handler(
    message: Message,
    command: CommandObject,
    session: AsyncSession,
    state: FSMContext,
    user: User | None,
):
    raise NotImplementedError


@router.message(CommandStart(), StateFilter(default_state))
async def command_start(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
) -> None:
    raise NotImplementedError

