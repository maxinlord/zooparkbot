from aiogram.types import Message, CallbackQuery, FSInputFile
from aiogram import F, Router
from tools import get_text_message
from sqlalchemy.ext.asyncio import AsyncSession
from db import Photo
from aiogram.fsm.context import FSMContext
from bot.states import UserState


router = Router()


# @router.message(F.text == 'test')
# async def test(
#     message: Message
# ) -> None:
#     pass


@router.message(F.content_type == "photo")
async def photo_catch(message: Message, session: AsyncSession) -> None:
    photo_id = message.photo[-1].file_id
    session.add(Photo(name=f"new_photo_{message.message_id}", photo_id=photo_id))
    await session.commit()
    await message.answer(text=await get_text_message("photo_saved"))


@router.message()
async def any_unknown_message(message: Message, state: FSMContext) -> None:
    await message.answer(text=await get_text_message("answer_on_unknown_message"))
    print(message.chat.id)



# @router.channel_post()
# async def any_unknown_channel_post(message: Message) -> None:
#     print(message.chat.id)


@router.callback_query()
async def any_unknown_callback(query: CallbackQuery) -> None:
    await query.message.edit_reply_markup(reply_markup=None)
