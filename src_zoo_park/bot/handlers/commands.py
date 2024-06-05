from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import mention_html

router = Router()


@router.message(Command(commands="usd"), StateFilter(any_state))
async def command_reset(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if not command.args:
        await message.answer("Не указана сумма и username")
        return
    args = command.args.split(" ")
    if len(args) < 2:
        await message.answer("Не указана сумма или username")
        return
    user_to_add = await session.scalar(select(User).where(User.username == args[1]))
    if not user_to_add:
        await message.answer("Пользователь не найден")
        return
    amount = int(args[0])
    user.usd += amount
    await session.commit()
    mention = mention_html(id_user=user_to_add.id_user, name=user_to_add.nickname)
    await message.answer(f"Добавлено {amount} USD игроку {mention}")
