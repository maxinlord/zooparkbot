from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tools import get_text_button


async def ik_back():
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button("back"), callback_data="back")
    return builder.as_markup()


async def ik_start_game(link: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button("start_zoopark_by_link"), url=link)
    return builder.as_markup()


async def ik_start_created_game(link: str, current_gamers: int, total_gamers: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button(
            "start_game_by_link",
            current_gamers=current_gamers,
            total_gamers=total_gamers,
        ),
        url=link,
    )
    return builder.as_markup()


async def rk_back():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button("back"))
    return builder.as_markup(resize_keyboard=True)


async def rk_cancel():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button("cancel"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)
