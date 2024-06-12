import contextlib
from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Animal, Item
from tools import (
    get_text_message,
    count_page_items,
    disable_not_main_window,
    income_,
    get_total_number_seats,
    get_remain_seats,
    activate_item,
    deactivate_all_items,
    get_status_item,
    get_total_number_animals,
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    rk_back,
    ik_choice_animal_rshop,
    ik_choice_rarity_rshop,
    ik_choice_quantity_animals_rshop,
    ik_account_menu,
    ik_menu_items,
    ik_item_activate_menu,
)
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

    total_places, remain_places, income, ik_account_menu_k = await asyncio.gather(
        get_total_number_seats(session=session, aviaries=user.aviaries),
        get_remain_seats(
            session=session,
            aviaries=user.aviaries,
            amount_animals=await get_total_number_animals(self=user),
        ),
        income_(session=session, user=user),
        ik_account_menu(),
    )
    
    text_message = await get_text_message(
        "account_info",
        nn=user.nickname,
        rub=user.rub,
        usd=user.usd,
        pawc=user.paw_coins,
        animals=user.animals,
        aviaries=user.aviaries,
        total_places=total_places,
        remain_places=remain_places,
        items=user.items,
        income=income,
    )

    msg = await message.answer(
        text=text_message,
        reply_markup=ik_account_menu_k,
    )

    await state.set_data({})
    await state.update_data(active_window=msg.message_id)


@router.callback_query(UserState.main_menu, F.data == "items")
async def account_items(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    q_page = await count_page_items(user.items)
    await state.update_data(page=1, q_page=q_page)
    await query.message.edit_text(
        text=await get_text_message("menu_items"),
        reply_markup=await ik_menu_items(session=session,
            items=user.items,
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
            reply_markup=await ik_menu_items(session=session,
                items=user.items,
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
                    animals=user.animals,
                    aviaries=user.aviaries,
                    total_places=await get_total_number_seats(
                        session=session, aviaries=user.aviaries
                    ),
                    remain_places=await get_remain_seats(
                        session=session,
                        aviaries=user.aviaries,
                        amount_animals=await get_total_number_animals(self=user),
                    ),
                    items=user.items,
                    income=await income_(session=session, user=user),
                ),
                reply_markup=await ik_account_menu(),
            )
        case "to_items":
            data = await state.get_data()
            await query.message.edit_text(
                text=await get_text_message("menu_items"),
                reply_markup=await ik_menu_items(session=session, items=user.items, page=data["page"]),
            )


@router.callback_query(UserState.main_menu, CompareDataByIndex("tap_item"))
async def process_viewing_item(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    code_name_item = query.data.split(":")[0]
    await state.update_data(code_name_item=code_name_item)
    item: Item = await session.scalar(
        select(Item).where(Item.code_name == code_name_item)
    )
    await query.message.edit_text(
        text=await get_text_message(
            "description_item",
            name_=item.description,
            description=item.description,
        ),
        reply_markup=await ik_item_activate_menu(
            await get_status_item(user, code_name_item)
        ),
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
    match query.data:
        case "item_activate":
            await deactivate_all_items(user)
            await activate_item(user, data["code_name_item"])
        case "item_deactivate":
            await activate_item(user, data["code_name_item"], False)
    await session.commit()
    item = await session.scalar(
        select(Item).where(Item.code_name == data["code_name_item"])
    )
    await query.message.edit_text(
        text=await get_text_message(
            "description_item",
            name_=item.description,
            description=item.description,
        ),
        reply_markup=await ik_item_activate_menu(
            await get_status_item(user, data["code_name_item"])
        ),
    )
