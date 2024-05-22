from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tools import get_text_button


async def ik_back():
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button('back'), callback_data='back')
    return builder.as_markup()


async def rk_back():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button('back'))
    return builder.as_markup(resize_keyboard=True)

async def rk_cancel():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button('cancel'))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)