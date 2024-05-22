from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tools import get_text_button


async def rk_main_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button("zoomarket"))
    builder.button(text=await get_text_button("unity"))
    builder.button(text=await get_text_button("account"))
    builder.button(text=await get_text_button("top"))
    builder.button(text=await get_text_button("bonus"))

    builder.adjust(2, 2, 1)
    return builder.as_markup(resize_keyboard=True)

async def rk_zoomarket_menu():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button("random_merchant"))
    builder.button(text=await get_text_button("rarity_shop"))
    builder.button(text=await get_text_button("workshop_items"))
    builder.button(text=await get_text_button("back"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)

