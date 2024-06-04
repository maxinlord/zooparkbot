


import contextlib
from aiogram.types import Message


async def disable_not_main_window(data: dict, message: Message):
    if data.get("active_window"):
        with contextlib.suppress(Exception):
            await message.bot.edit_message_reply_markup(
                chat_id=message.chat.id,
                message_id=data["active_window"],
                reply_markup=None,
            )