import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Unity
from tools import (
    get_text_message,
    disable_not_main_window,
    count_page_unity_members,
    income_,
    get_total_number_animals
)
from bot.states import UserState
from bot.keyboards import (
    ik_menu_unity_members,
    ik_member_menu,
    ik_back_member,
)
from bot.filters import GetTextButton, CompareDataByIndex

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.unity_menu, GetTextButton("unity_members"), flags=flags)
async def unity_members(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    data = await state.get_data()
    q_page = await count_page_unity_members(idpk_unity=data["idpk_unity"])
    msg = await message.answer(
        text=await get_text_message("menu_unity_members"),
        reply_markup=await ik_menu_unity_members(session=session, unity_idpk=data["idpk_unity"]),
    )
    await state.update_data(
        active_window=msg.message_id,
        page=1,
        q_page=q_page,
    )


@router.callback_query(UserState.unity_menu, CompareDataByIndex("unity_member"))
async def process_turn_unity_members(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    page = data["page"]
    side = query.data.split(":")[0]
    if side == "left":
        page = page - 1 if page > 1 else data["q_page"]
    else:
        page = page + 1 if page < data["q_page"] else 1
    await state.update_data(page=page)
    with contextlib.suppress(Exception):
        await query.message.edit_reply_markup(
            reply_markup=await ik_menu_unity_members(session=session,
                unity_idpk=data["idpk_unity"], page=page
            )
        )


@router.callback_query(UserState.unity_menu, CompareDataByIndex("tap_member"))
async def process_viewing_member_bio(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    idpk = int(query.data.split(":")[0])
    member = await session.get(User, idpk)
    rule = user.current_unity.split(":")[0]
    await state.update_data(idpk_member=idpk, id_member=member.id_user)
    keyboard = (
        await ik_member_menu()
        if rule == "owner" and idpk != user.idpk
        else await ik_back_member()
    )
    await query.message.edit_text(
        text=await get_text_message(
            "member_bio",
            nickname=member.nickname,
            income=await income_(session=session, user=member),
            rub=member.rub,
            usd=member.usd,
            amount_animals=await get_total_number_animals(self=member),
        ),
        reply_markup=keyboard,
    )


@router.callback_query(UserState.unity_menu, CompareDataByIndex("back_unity_members"))
async def process_back_to_menu_all_members(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_all_members":
            data = await state.get_data()
            q_page = await count_page_unity_members(idpk_unity=data["idpk_unity"])
            await state.update_data(q_page=q_page)
            await query.message.edit_text(
                text=await get_text_message("menu_unity_members"),
                reply_markup=await ik_menu_unity_members(session=session,
                    unity_idpk=data["idpk_unity"], page=data["page"]
                ),
            )


@router.callback_query(UserState.unity_menu, F.data == "delete_from_members")
async def delete_from_members(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    unity = await session.get(Unity, data["idpk_unity"])
    unity.remove_member(idpk_member=str(data["idpk_member"]))
    member = await session.get(User, data["idpk_member"])
    member.current_unity = None
    await session.commit()
    await query.message.edit_text(
        text=await get_text_message("menu_unity_members"),
        reply_markup=await ik_menu_unity_members(session=session, unity_idpk=data["idpk_unity"], page=1),
    )
    await query.bot.send_message(
        chat_id=data["id_member"],
        text=await get_text_message("delete_from_members_text"),
    )
