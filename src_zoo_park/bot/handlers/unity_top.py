from aiogram import Router
from aiogram.fsm.context import FSMContext
from aiogram.types import Message
from bot.filters import GetTextButton
from bot.states import UserState
from db import Animal, Unity, User
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from tools import (
    factory_text_unity_top,
    get_text_message,
    get_top_unity_by_animal,
    get_value,
)

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.unity_menu, GetTextButton("top_unity"), flags=flags)
async def unity_members(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    tops = await factory_text_unity_top(session=session)
    unity_idpk, animal_dict = await get_top_unity_by_animal(session=session)
    unity = await session.get(Unity, unity_idpk)
    code_name_animal, amount_animal = list(animal_dict.items())[0]
    animal_name = await session.scalar(
        select(Animal.name).where(Animal.code_name == code_name_animal)
    )
    BONUS_FOR_AMOUNT_ANIMALS = await get_value(
        session=session, value_name="BONUS_FOR_AMOUNT_ANIMALS"
    )
    await message.answer(
        text=await get_text_message(
            "unity_top_10",
            name_unity=unity.format_name,
            animal_name=animal_name,
            amount_animal=amount_animal,
            bonus=BONUS_FOR_AMOUNT_ANIMALS,
            t=tops,
        )
    )
