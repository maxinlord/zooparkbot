from aiogram.types import Message, CallbackQuery
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Item
from tools import get_text_message, disable_not_main_window, add_to_currency, add_to_amount_expenses_currency, add_item
from bot.states import UserState
from bot.keyboards import (
    ik_choice_item,
    ik_buy_item,
)
from bot.filters import GetTextButton, CompareDataByIndex
from config import dict_tr_currencys

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.zoomarket_menu, GetTextButton("workshop_items"), flags=flags)
async def workshop_items_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    msg = await message.answer(
        text=await get_text_message("workshop_items_menu"),
        reply_markup=await ik_choice_item(),
    )
    await state.set_data({})
    await state.update_data(active_window=msg.message_id)


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("choice_item_witems")
)
async def witems_menu_choice_item(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    item: str = query.data.split(":")[0]
    await state.update_data(code_name_item=item)
    item: Item = await session.scalar(select(Item).where(Item.code_name == item))
    await query.message.edit_text(
        text=await get_text_message(
            "witems_menu_buy_item",
            name_=item.name,
            description=item.description,
            price=item.price,
            currency=dict_tr_currencys[item.currency],
        ),
        reply_markup=await ik_buy_item(),
    )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("back_witems"))
async def distribution_back_witems(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_witems_menu":
            await query.message.edit_text(
                text=await get_text_message("workshop_items_menu"),
                reply_markup=await ik_choice_item(),
            )


@router.callback_query(UserState.zoomarket_menu, F.data == "buy_item")
async def buy_item(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    item: Item = await session.scalar(
        select(Item).where(Item.code_name == data["code_name_item"])
    )
    if item.code_name in user.items:
        await query.answer(await get_text_message("item_already_have"), show_alert=True)
        return
    if user.get_currency(item.currency) < item.price:
        await query.answer(
            await get_text_message("not_enough_money"),
            show_alert=True,
        )
        return
    await add_to_currency(self=user, currency=item.currency, amount=-item.price)
    await add_to_amount_expenses_currency(self=user, currency=item.currency, amount=item.price)
    await add_item(self=user, code_name_item=item)

    await session.commit()
    await query.answer(
        text=await get_text_message("item_bought_successful"), show_alert=True
    )
