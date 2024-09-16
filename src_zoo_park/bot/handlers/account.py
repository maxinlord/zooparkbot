import contextlib
import json
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func
from db import User, Item
from tools import (
    get_text_message,
    count_page_items,
    disable_not_main_window,
    income_,
    get_total_number_seats,
    get_remain_seats,
    get_total_number_animals,
    factory_text_account_animals,
    factory_text_account_aviaries,
    ft_item_props,
    synchronize_info_about_items,
)
from bot.states import UserState
from bot.keyboards import ik_account_menu, ik_menu_items, ik_item_activate_menu, ik_back
from bot.filters import GetTextButton, CompareDataByIndex

flags = {"throttling_key": "default"}
router = Router()


import asyncio


@router.message(UserState.main_menu, GetTextButton("account"), flags=flags)
async def account(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)

    income, ik_account_menu_k = await asyncio.gather(
        income_(session=session, user=user),
        ik_account_menu(),
    )

    text_message = await get_text_message(
        "account_info",
        nn=user.nickname,
        rub=user.rub,
        usd=user.usd,
        pawc=user.paw_coins,
        income=income,
    )

    msg = await message.answer(
        text=text_message,
        reply_markup=ik_account_menu_k,
    )

    await state.set_data({})
    await state.update_data(active_window=msg.message_id)


@router.callback_query(UserState.main_menu, F.data == "account_animals")
async def account_animals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    if user.animals == "{}":
        await query.answer(
            text=await get_text_message("no_animals"),
            show_alert=True,
        )
        return
    text = await factory_text_account_animals(session=session, animals=user.animals)
    await query.message.edit_text(
        text=await get_text_message(
            "account_animals",
            t=text,
            total_animals=await get_total_number_animals(user),
        ),
        reply_markup=await ik_back(custom_callback_data="to_account:back_account"),
    )


@router.callback_query(UserState.main_menu, F.data == "account_aviaries")
async def account_aviaries(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    if user.aviaries == "{}":
        await query.answer(
            text=await get_text_message("no_aviaries"),
            show_alert=True,
        )
        return
    text, total_places, remain_places = await asyncio.gather(
        factory_text_account_aviaries(session=session, aviaries=user.aviaries),
        get_total_number_seats(session=session, aviaries=user.aviaries),
        get_remain_seats(
            session=session,
            user=user,
        ),
    )
    await query.message.edit_text(
        text=await get_text_message(
            "account_aviaries",
            t=text,
            total_places=total_places,
            remain_places=remain_places,
        ),
        reply_markup=await ik_back(custom_callback_data="to_account:back_account"),
    )


@router.callback_query(UserState.main_menu, F.data == "items")
async def account_items(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    amount_items = await session.scalar(
        select(func.count()).select_from(Item).where(Item.id_user == user.id_user)
    )
    if amount_items == 0:
        await query.answer(
            text=await get_text_message("no_items"),
            show_alert=True,
        )
        return
    q_page = await count_page_items(session=session, amount_items=amount_items)
    await state.update_data(page=1, q_page=q_page)
    await query.message.edit_text(
        text=await get_text_message("menu_items"),
        reply_markup=await ik_menu_items(
            session=session,
            id_user=user.id_user,
        ),
    )


@router.callback_query(UserState.main_menu, F.data.in_(["right", "left"]))
async def process_turn_right(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    page = data["page"]
    if query.data == "left":
        page = page - 1 if page > 1 else data["q_page"]
    else:
        page = page + 1 if page < data["q_page"] else 1
    await state.update_data(page=page)
    with contextlib.suppress(Exception):
        await query.message.edit_reply_markup(
            reply_markup=await ik_menu_items(
                session=session,
                id_user=user.id_user,
                page=page,
            ),
        )


@router.callback_query(UserState.main_menu, CompareDataByIndex("back_account"))
async def process_back_to_menu(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_account":
            await query.message.edit_text(
                text=await get_text_message(
                    "account_info",
                    nn=user.nickname,
                    rub=user.rub,
                    usd=user.usd,
                    pawc=user.paw_coins,
                    income=await income_(session=session, user=user),
                ),
                reply_markup=await ik_account_menu(),
            )
        case "to_items":
            data = await state.get_data()
            await query.message.edit_text(
                text=await get_text_message("menu_items"),
                reply_markup=await ik_menu_items(
                    session=session, id_user=user.id_user, page=data["page"]
                ),
            )


@router.callback_query(UserState.main_menu, CompareDataByIndex("tap_item"))
async def process_viewing_item(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    id_item = query.data.split(":")[0]
    await state.update_data(id_item=id_item)
    item: Item = await session.scalar(select(Item).where(Item.id_item == id_item))
    props = await ft_item_props(item_props=item.properties)
    await query.message.edit_text(
        text=await get_text_message(
            "description_item",
            name_=item.name_with_emoji,
            description=props,
        ),
        reply_markup=await ik_item_activate_menu(is_activate=item.is_active),
    )


@router.callback_query(
    UserState.main_menu, F.data.in_(["item_activate", "item_deactivate"])
)
async def process_viewing_recipes(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    is_activate = True
    items = await session.scalars(
        select(Item).where(Item.id_user == user.id_user, Item.is_active == True)
    )
    items = list(items.all())
    if query.data == "item_activate":
        if len(items) == 3:
            await query.answer(
                text=await get_text_message("max_active_items"),
                show_alert=True,
            )
            return
        item: Item = await session.scalar(
            select(Item).where(Item.id_item == data["id_item"])
        )
        item.is_active = True
        items.append(item)
    elif query.data == "item_deactivate":
        is_activate = False
        item: Item = await session.scalar(
            select(Item).where(Item.id_item == data["id_item"])
        )
        item.is_active = False
        items.remove(item)
    user.info_about_items = await synchronize_info_about_items(items=items)
    await session.commit()
    await query.message.edit_reply_markup(
        reply_markup=await ik_item_activate_menu(is_activate=is_activate),
    )
