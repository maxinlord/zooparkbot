from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from tools import get_text_message
from sqlalchemy.ext.asyncio import AsyncSession
from db import Photo
router = Router()


# @router.message(F.text == 'test')
# async def test(
#     message: Message
# ) -> None:
#     pass


@router.message(F.content_type == 'photo')
async def photo_catch(message: Message, session: AsyncSession) -> None:
    photo_id = message.photo[-1].file_id
    session.add(Photo(name=f'new_photo_{message.message_id}', photo_id=photo_id))
    await session.commit()
    await message.answer(text=await get_text_message("photo_saved"))

@router.message()
async def any_unknown_message(message: Message) -> None:
    await message.answer(text=await get_text_message("answer_on_unknown_message"))


@router.callback_query()
async def any_unknown_callback(query: CallbackQuery) -> None:
    await query.message.edit_reply_markup(reply_markup=None)
