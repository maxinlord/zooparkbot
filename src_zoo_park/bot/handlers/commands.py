from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state

router = Router()


@router.message(Command(commands='reset'), StateFilter(any_state))
async def command_reset(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    await state.clear()