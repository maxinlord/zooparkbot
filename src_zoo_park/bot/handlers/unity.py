import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import Router, F
from aiogram.fsm.context import FSMContext
from aiogram.fsm.state import any_state
from aiogram.filters import StateFilter
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Unity, Value, RequestToUnity
from datetime import datetime
from tools import (
    get_text_message,
    has_special_characters_name,
    shorten_whitespace_name_unity,
    is_unique_name,
    disable_not_main_window,
    count_page_unity,
    get_value,
    income_,
    get_total_number_animals,
    mention_html,
)
from bot.states import UserState
from bot.keyboards import (
    rk_unity_menu,
    rk_main_menu,
    ik_unity_options,
    rk_back,
    ik_menu_unity_to_join,
    ik_unity_invitation,
    ik_unity_send_request,
)
from bot.filters import GetTextButton, CompareDataByIndex
from datetime import timedelta

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.main_menu, GetTextButton("unity"), flags=flags)
async def unity_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    if user.current_unity:
        idpk_unity = int(user.current_unity.split(":")[-1])
        unity: Unity = await session.get(Unity, idpk_unity)
        await state.set_state(UserState.unity_menu)
        await state.update_data(idpk_unity=unity.idpk)
        await message.answer(
            text=await get_text_message("unity_menu"),
            reply_markup=await rk_unity_menu(),
        )
        return
    PRICE_FOR_CREATE_UNITY = await get_value(
        session=session, value_name="PRICE_FOR_CREATE_UNITY"
    )
    await state.update_data(price_fcu=PRICE_FOR_CREATE_UNITY)
    msg = await message.answer(
        text=await get_text_message("unity_options"),
        reply_markup=await ik_unity_options(price_create=PRICE_FOR_CREATE_UNITY),
    )
    await state.update_data(active_window=msg.message_id)


@router.message(UserState.unity_menu, GetTextButton("back"))
async def back_to_main_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )


@router.callback_query(UserState.main_menu, F.data == "create_unity")
async def create_unity(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    if user.usd < data["price_fcu"]:
        await query.answer(
            await get_text_message("not_enough_money_to_create"),
            show_alert=True,
        )
        return
    await state.set_state(UserState.enter_name_unity_step)
    await query.message.delete()
    await query.message.answer(
        text=await get_text_message("enter_name_unity"),
        reply_markup=await rk_back(),
    )


@router.message(UserState.enter_name_unity_step, GetTextButton("back"))
async def back_to_main_menu_2(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )


@router.message(UserState.enter_name_unity_step)
async def get_name_unity(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    LIMIT_LENGTH_MAX = await get_value(
        session=session, value_name="NAME_UNITY_LENGTH_MAX"
    )
    LIMIT_LENGTH_MIN = await get_value(
        session=session, value_name="NAME_UNITY_LENGTH_MIN"
    )
    if len(message.text) > LIMIT_LENGTH_MAX:
        await message.answer(text=await get_text_message("name_unity_too_long"))
        return
    if len(message.text) < LIMIT_LENGTH_MIN:
        await message.answer(text=await get_text_message("name_unity_too_short"))
        return
    if chars := await has_special_characters_name(message.text):
        await message.answer(
            text=await get_text_message(
                "name_unity_has_special_characters", chars=chars
            )
        )
        return
    if not await is_unique_name(session=session, nickname=message.text):
        await message.answer(text=await get_text_message("nickname_not_unique"))
        return
    data = await state.get_data()
    user.usd -= data["price_fcu"]
    user.amount_expenses_usd += data["price_fcu"]
    name_unity = await shorten_whitespace_name_unity(message.text)
    unity = Unity(idpk_user=user.idpk, name=name_unity)
    session.add(unity)
    await session.flush()
    user.current_unity = f"owner:{unity.idpk}"
    await session.commit()
    await state.set_state(UserState.unity_menu)
    await state.update_data(idpk_unity=unity.idpk)
    await message.answer(
        text=await get_text_message("unity_menu"),
        reply_markup=await rk_unity_menu(),
    )


@router.callback_query(UserState.main_menu, F.data == "join_to_unity")
async def join_to_unity(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    q_page = await count_page_unity(session=session)
    if q_page == 0:
        await query.answer(
            text=await get_text_message("no_unity_to_join"), show_alert=True
        )
        return
    await state.update_data(q_page=q_page, page=1)
    await query.message.edit_text(
        text=await get_text_message("join_to_unity_menu"),
        reply_markup=await ik_menu_unity_to_join(session=session, page=1),
    )


@router.callback_query(UserState.main_menu, CompareDataByIndex("unity"))
async def process_turn_unity(
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
            reply_markup=await ik_menu_unity_to_join(session=session, page=page)
        )


@router.callback_query(UserState.main_menu, CompareDataByIndex("back_unity"))
async def process_back_to_menu_all_unity(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_menu_unity":
            data = await state.get_data()
            await query.message.edit_text(
                text=await get_text_message("unity_options"),
                reply_markup=await ik_unity_options(data["price_fcu"]),
            )
        case "to_all_unity":
            q_page = await count_page_unity(session=session)
            await state.update_data(q_page=q_page, page=1)
            await query.message.edit_text(
                text=await get_text_message("join_to_unity_menu"),
                reply_markup=await ik_menu_unity_to_join(session=session, page=1),
            )


@router.callback_query(UserState.main_menu, CompareDataByIndex("tap_unity"))
async def process_viewing_unity_bio(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    idpk_owner = int(query.data.split(":")[0])
    unity = await session.scalar(select(Unity).where(Unity.idpk_user == idpk_owner))
    owner = await session.get(User, idpk_owner)
    await state.update_data(idpk_owner=idpk_owner)
    await query.message.edit_text(
        text=await get_text_message(
            "description_unity",
            name_=unity.name,
            lvl=unity.level,
            nickname_owner=owner.nickname,
            owner_income=await income_(session=session, user=owner),
        ),
        reply_markup=await ik_unity_send_request(),
    )


@router.callback_query(UserState.main_menu, F.data == "request_unity")
async def process_send_request(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:

    if await session.scalar(
        select(RequestToUnity).where(RequestToUnity.idpk_user == user.idpk)
    ):
        await query.answer(
            text=await get_text_message("already_send_request"), show_alert=True
        )
        return
    data = await state.get_data()
    unity_owner: User = await session.get(User, data["idpk_owner"])
    await query.message.edit_text(
        text=await get_text_message("request_send"),
        reply_markup=None,
    )
    MIN_TO_END_REQUEST = await get_value(
        session=session, value_name="MIN_TO_END_REQUEST"
    )
    date_request_end = datetime.now() + timedelta(minutes=MIN_TO_END_REQUEST)
    request = RequestToUnity(
        idpk_user=user.idpk,
        idpk_unity_owner=unity_owner.idpk,
        date_request=datetime.now(),
        date_request_end=date_request_end,
    )
    session.add(request)
    await session.commit()
    await query.bot.send_message(
        chat_id=unity_owner.id_user,
        text=await get_text_message(
            "request_add_to_unity",
            nickname=mention_html(id_user=user.id_user, name=user.nickname),
            usd=user.usd,
            rub=user.rub,
            animals=await get_total_number_animals(self=user),
            income=await income_(session=session, user=user),
        ),
        reply_markup=await ik_unity_invitation(user.idpk),
    )


@router.callback_query(StateFilter(any_state), CompareDataByIndex("accept_to_unity"))
async def process_accept_to_unity(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    unity: Unity = await session.scalar(
        select(Unity).where(Unity.idpk_user == user.idpk)
    )
    member: int = int(query.data.split(":")[0])
    member: User = await session.get(User, member)
    member.current_unity = f"member:{unity.idpk}"
    r = await session.scalar(
        select(RequestToUnity).where(RequestToUnity.idpk_user == member.idpk)
    )
    if r:
        await session.delete(r)
    unity.add_member(idpk_member=member.idpk)
    await session.commit()
    await query.message.edit_text(
        text=await get_text_message("request_accepted"),
        reply_markup=None,
    )
    await query.bot.send_message(
        chat_id=member.id_user,
        text=await get_text_message("request_accepted_to_unity"),
    )


@router.callback_query(StateFilter(any_state), CompareDataByIndex("rejected_to_unity"))
async def process_accept_to_unity(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    member: int = int(query.data.split(":")[0])
    member: User = await session.get(User, member)
    r = await session.scalar(
        select(RequestToUnity).where(RequestToUnity.idpk_user == member.idpk)
    )
    await session.delete(r)
    await session.commit()
    await query.message.edit_text(
        text=await get_text_message("request_rejected"),
        reply_markup=None,
    )
    await query.bot.send_message(
        chat_id=member.id_user,
        text=await get_text_message("request_rejected_to_unity"),
    )


@router.message(UserState.unity_menu, GetTextButton("exit_from_unity"))
async def exit_from_unity(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    unity = await session.get(Unity, data["idpk_unity"])
    # если не владелец объединения
    if unity.idpk_user != user.idpk:
        unity.remove_member(idpk_member=str(user.idpk))
        user.current_unity = None
        await state.set_state(UserState.main_menu)
        await session.commit()
        await message.answer(
            text=await get_text_message("exit_from_unity_text"), reply_markup=None
        )
        await message.answer(
            text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
        )
        return
    # если владелец объединения
    user.current_unity = None
    idpk_next_owner = unity.remove_first_member()
    if idpk_next_owner:
        next_owner: User = await session.get(User, idpk_next_owner)
        next_owner.current_unity = f"owner:{unity.idpk}"
        unity.idpk_user = next_owner.idpk
        await message.answer(
            text=await get_text_message("exit_from_unity_text"), reply_markup=None
        )
        await message.bot.send_message(
            chat_id=next_owner.id_user,
            text=await get_text_message("you_new_owner_unity"),
        )
    else:
        await session.delete(unity)
        await message.answer(
            text=await get_text_message("unity_deleted"), reply_markup=None
        )
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("main_menu"), reply_markup=await rk_main_menu()
    )
    await session.commit()
