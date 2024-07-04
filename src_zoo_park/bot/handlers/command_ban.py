from aiogram.filters import CommandObject, Command
from aiogram.types import Message
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, BlackList
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import (
    mention_html,
)
from config import CHAT_ID

router = Router()
flags = {"throttling_key": "default"}


# @router.resolve_used_update_types(Command(commands="ban"), StateFilter(any_state), flags=flags)
# async def command_ban(
#     message: Message,
#     state: FSMContext,
#     command: CommandObject,
#     session: AsyncSession,
#     user: User | None,
# ) -> None:
#     print(message.reply_to_message.from_user.id)
#     if not command.args:
#         id_to_ban = message.forward_from.id
#         session.add(
#             BlackList(
#                 id_user=id_to_ban,
#             )
#         )
#         await session.commit()
#         return
#     # args = command.args.split(" ")
#     # if len(args) < 2:
#     #     await message.answer("Не указана сумма или username")
#     #     return
#     # user_to_add = await session.scalar(select(User).where(User.username == args[1]))
#     # if not user_to_add:
#     #     await message.answer("Пользователь не найден")
#     #     return
#     # amount = int(args[0])
