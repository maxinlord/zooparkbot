from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Unity
from tools import (
    get_text_message,
    disable_not_main_window,
    check_condition_1st_lvl,
    check_condition_2nd_lvl,
    check_condition_3rd_lvl,
    get_data_by_lvl_unity,
)
from bot.states import UserState
from bot.keyboards import (
    ik_update_level_unity,
)
from bot.filters import GetTextButton

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.unity_menu, GetTextButton("level"), flags=flags)
async def unity_level(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    data = await state.get_data()
    unity = await session.get(Unity, data["idpk_unity"])
    data_for_text = await get_data_by_lvl_unity(
        session=session, lvl=unity.level, unity=unity
    )
    msg = await message.answer(
        text=await get_text_message(f"unity_level_{unity.level}", **data_for_text),
        reply_markup=await ik_update_level_unity(),
    )
    await state.update_data(active_window=msg.message_id)


@router.callback_query(UserState.unity_menu, F.data == "update_level_unity")
async def update_unity_level(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    unity = await session.get(Unity, data["idpk_unity"])
    match unity.level:
        case 0:
            pass_to_up = await check_condition_1st_lvl(session=session, unity=unity)
            if not pass_to_up:
                await query.answer(
                    text=await get_text_message("conditions_are_not_met"),
                    show_alert=True,
                )
                return
            unity.level = 1
        case 1:
            pass_to_up = await check_condition_2nd_lvl(session=session, unity=unity)
            if not pass_to_up:
                await query.answer(
                    text=await get_text_message("conditions_are_not_met"),
                    show_alert=True,
                )
                return
            unity.level = 2
        case 2:
            pass_to_up = await check_condition_3rd_lvl(session=session, unity=unity)
            if not pass_to_up:
                await query.answer(
                    text=await get_text_message("conditions_are_not_met"),
                    show_alert=True,
                )
                return

            unity.level = 3
        case 3:
            await query.answer(
                text=await get_text_message("unity_level_max"),
                show_alert=True,
            )
            return
    await session.commit()
    data_for_text = await get_data_by_lvl_unity(
        session=session, lvl=unity.level, unity=unity
    )
    await query.message.edit_text(
        text=await get_text_message(f"unity_level_{unity.level}", **data_for_text),
        reply_markup=await ik_update_level_unity(),
    )
