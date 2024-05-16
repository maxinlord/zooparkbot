from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tools import get_text_button


async def k_back():
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button('back'), callback_data='back')
    return builder.as_markup()


async def k_back_reply():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button('back'))
    return builder.as_markup(resize_keyboard=True)

async def k_cancel():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button('cancel'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)