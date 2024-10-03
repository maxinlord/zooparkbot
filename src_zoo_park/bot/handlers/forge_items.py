import contextlib
import json

from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import CallbackQuery, Message
from bot.filters import CompareDataByIndex, GetTextButton
from bot.keyboards import (
    ik_choice_items_to_merge,
    ik_create_item,
    ik_forge_items_menu,
    ik_menu_items_for_merge,
    ik_menu_items_for_up,
    ik_up_lvl_item,
    ik_upgrade_item,
)
from bot.states import UserState
from db import Item, User
from game_variables import prop_quantity_by_rarity, translated_rarities
from sqlalchemy import and_, func, select
from sqlalchemy.ext.asyncio import AsyncSession
from tools import (
    able_to_enhance,
    add_item_to_db,
    calculate_percent_to_enhance,
    count_page_items,
    create_item,
    disable_not_main_window,
    fetch_and_parse_str_value,
    ft_item_props,
    ft_item_props_for_update,
    gen_price_to_create_item,
    get_text_message,
    get_value,
    merge_items,
    random_up_property_item,
    synchronize_info_about_items,
    update_prop_iai,
)

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.zoomarket_menu, GetTextButton("forge_items"), flags=flags)
async def forge_items_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    msg = await message.answer(
        text=await get_text_message("forge_items_menu", usd=user.usd),
        reply_markup=await ik_forge_items_menu(),
    )
    await state.set_data({})
    await state.update_data(active_window=msg.message_id)


@router.callback_query(UserState.zoomarket_menu, F.data == "create_item_info")
async def fi_create_item_info(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    USD_TO_CREATE_ITEM = await gen_price_to_create_item(
        session=session, id_user=user.id_user
    )
    common, rare, epic, mythical = await fetch_and_parse_str_value(
        session=session,
        value_name="WEIGHT_RARITIES_ITEM",
        func_to_element=lambda x: int(float(x) * 100),
    )
    await state.update_data(USD_TO_CREATE_ITEM=USD_TO_CREATE_ITEM)
    await query.message.edit_text(
        text=await get_text_message(
            "item_probability_info",
            uci=int(USD_TO_CREATE_ITEM),
            common_weight=common,
            rare_weight=rare,
            epic_weight=epic,
            mythical_weight=mythical,
        ),
        reply_markup=await ik_create_item(),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "create_item")
async def fi_create_item(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    USD_TO_CREATE_ITEM = (await state.get_data())["USD_TO_CREATE_ITEM"]
    if user.usd < USD_TO_CREATE_ITEM:
        await query.answer(
            text=await get_text_message("not_enough_usd"), show_alert=True
        )
        return
    user.usd -= USD_TO_CREATE_ITEM
    user.amount_expenses_usd += USD_TO_CREATE_ITEM
    item_info, item_props = await create_item(session=session)
    await add_item_to_db(
        session=session,
        item_info=item_info,
        item_props=item_props,
        id_user=user.id_user,
    )
    await session.commit()
    USD_TO_CREATE_ITEM = await gen_price_to_create_item(
        session=session, id_user=user.id_user
    )
    await state.update_data(USD_TO_CREATE_ITEM=USD_TO_CREATE_ITEM)
    text_props = await ft_item_props(item_props=item_props)
    await query.message.edit_text(
        text=await get_text_message(
            "item_created",
            name_=item_info["name"],
            emoji=item_info["emoji"],
            rarity=translated_rarities[item_info["rarity"]],
            text_props=text_props,
        ),
        reply_markup=await ik_create_item(uci=USD_TO_CREATE_ITEM),
    )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("back_forge_items"))
async def process_back_forge_items(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_forge_items_menu":
            await query.message.edit_text(
                text=await get_text_message("forge_items_menu", usd=user.usd),
                reply_markup=await ik_forge_items_menu(),
            )
        case "to_up_lvl_item_info":
            PERCENTAGE_DECREASE_ENHANCE_BY_LVL = await get_value(
                session=session, value_name="PERCENTAGE_DECREASE_ENHANCE_BY_LVL"
            )
            await query.message.edit_text(
                text=await get_text_message(
                    "up_lvl_item_info",
                    usd=user.usd,
                    pd=PERCENTAGE_DECREASE_ENHANCE_BY_LVL,
                ),
                reply_markup=await ik_up_lvl_item(),
            )
        case "to_choice_item":
            data = await state.get_data()
            page = data["page"]
            await query.message.edit_text(
                text=await get_text_message("menu_items"),
                reply_markup=await ik_menu_items_for_up(
                    session=session,
                    id_user=user.id_user,
                    page=page,
                ),
            )
        case "to_merge_items_info":
            PERCENT_MERGE_BY_PROP = await get_value(
                session=session, value_name="PERCENT_MERGE_BY_PROP"
            )
            await query.message.edit_text(
                text=await get_text_message(
                    "merge_items_info", usd=user.usd, pm=PERCENT_MERGE_BY_PROP
                ),
                reply_markup=await ik_choice_items_to_merge(),
            )


@router.callback_query(UserState.zoomarket_menu, F.data == "up_lvl_item_info")
async def fi_up_lvl_item_info(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    PERCENTAGE_DECREASE_ENHANCE_BY_LVL = await get_value(
        session=session, value_name="PERCENTAGE_DECREASE_ENHANCE_BY_LVL"
    )
    await query.message.edit_text(
        text=await get_text_message(
            "up_lvl_item_info", usd=user.usd, pd=PERCENTAGE_DECREASE_ENHANCE_BY_LVL
        ),
        reply_markup=await ik_up_lvl_item(),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "choice_item_for_upgrade")
async def fi_choice_item_for_upgrade(
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
        reply_markup=await ik_menu_items_for_up(
            session=session,
            id_user=user.id_user,
        ),
    )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("up_items"))
async def process_turn_up_item(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    page = data["page"]
    turn_to = query.data.split(":")[0]
    if turn_to == "left":
        page = page - 1 if page > 1 else data["q_page"]
    else:
        page = page + 1 if page < data["q_page"] else 1
    await state.update_data(page=page)
    with contextlib.suppress(Exception):
        await query.message.edit_reply_markup(
            reply_markup=await ik_menu_items_for_up(
                session=session,
                id_user=user.id_user,
                page=page,
            ),
        )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("tap_to_up_item"))
async def process_viewing_to_up_item(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    id_item = query.data.split(":")[0]
    item: Item = await session.scalar(select(Item).where(Item.id_item == id_item))
    MAX_LVL_ITEM = await get_value(session=session, value_name="MAX_LVL_ITEM")
    if item.lvl == MAX_LVL_ITEM:
        await query.answer(
            text=await get_text_message("item_reached_max_lvl"), show_alert=True
        )
        return
    USD_TO_UP_ITEM = await get_value(session=session, value_name="USD_TO_UP_ITEM")
    USD_TO_UP_ITEM_view = USD_TO_UP_ITEM * (item.lvl + 1)
    await state.update_data(
        id_item=id_item,
        item_lvl=item.lvl,
        MAX_LVL_ITEM=MAX_LVL_ITEM,
        USD_TO_UP_ITEM=USD_TO_UP_ITEM,
    )
    penh = await calculate_percent_to_enhance(
        session=session, current_item_lvl=item.lvl
    )
    props = await ft_item_props(item_props=item.properties)
    await query.message.edit_text(
        text=await get_text_message(
            "description_item_to_up",
            name_=item.name_with_emoji,
            description=props,
            utui=USD_TO_UP_ITEM_view,
            penh=penh,
        ),
        reply_markup=await ik_upgrade_item(),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "upgrade_item")
async def fi_upgrade_item(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    if data["item_lvl"] == data["MAX_LVL_ITEM"]:
        await query.answer(
            text=await get_text_message("item_reached_max_lvl"), show_alert=True
        )
        return
    USD_TO_UP_ITEM = data["USD_TO_UP_ITEM"] * (data["item_lvl"] + 1)
    if user.usd < USD_TO_UP_ITEM:
        await query.answer(
            text=await get_text_message("not_enough_usd"), show_alert=True
        )
        return
    user.usd -= USD_TO_UP_ITEM
    user.amount_expenses_usd += USD_TO_UP_ITEM
    await session.commit()
    if not await able_to_enhance(session=session, current_item_lvl=data["item_lvl"]):
        await query.answer(text=await get_text_message("not_updated"), show_alert=False)
        return
    id_item = data["id_item"]
    item: Item = await session.scalar(select(Item).where(Item.id_item == id_item))
    new_item_properties, updated_property, parameter = await random_up_property_item(
        session=session, item_properties=item.properties
    )
    if item.is_active:
        user.info_about_items = await update_prop_iai(
            info_about_items=user.info_about_items,
            prop=updated_property,
            value=parameter,
        )
    item.properties = new_item_properties
    item.lvl += 1
    await state.update_data(item_lvl=item.lvl)
    await session.commit()
    utui = data["USD_TO_UP_ITEM"] * (item.lvl + 1)
    text_props = await ft_item_props_for_update(
        item_props=new_item_properties,
        updated_prop=updated_property,
        parameter=parameter,
    )
    penh = await calculate_percent_to_enhance(
        session=session, current_item_lvl=item.lvl
    )
    await query.message.edit_text(
        text=await get_text_message(
            "item_upgraded",
            name_=item.name_with_emoji,
            item_lvl=item.lvl,
            text_props=text_props,
            utui=utui,
            penh=penh,
        ),
        reply_markup=await ik_upgrade_item(),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "merge_items_info")
async def fi_merge_items_info(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    PERCENT_MERGE_BY_PROP = await get_value(
        session=session, value_name="PERCENT_MERGE_BY_PROP"
    )
    await query.message.edit_text(
        text=await get_text_message(
            "merge_items_info", usd=user.usd, pm=PERCENT_MERGE_BY_PROP
        ),
        reply_markup=await ik_choice_items_to_merge(),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "choice_item_to_merge")
async def fi_choice_item_to_merge(
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
    await state.update_data(
        page=1,
        q_page=q_page,
        id_chosen_items=[],
        status_chosen_items=[],
        q_props_items=[],
        lvl_items=[],
        ft_props=[],
    )
    await query.message.edit_text(
        text=await get_text_message("merge_menu_items"),
        reply_markup=await ik_menu_items_for_merge(
            session=session,
            id_user=user.id_user,
        ),
    )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("turn_merge_items"))
async def process_turn_merge_items(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    data = await state.get_data()
    page = data["page"]
    turn_to = query.data.split(":")[0]
    if turn_to == "left":
        page = page - 1 if page > 1 else data["q_page"]
    else:
        page = page + 1 if page < data["q_page"] else 1
    await state.update_data(page=page)
    with contextlib.suppress(Exception):
        await query.message.edit_reply_markup(
            reply_markup=await ik_menu_items_for_merge(
                session=session,
                id_user=user.id_user,
                page=page,
                id_chosen_items=data["id_chosen_items"],
            ),
        )


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("tap_to_merge_item")
)
async def process_viewing_to_merge_item(
    query: CallbackQuery,
    state: FSMContext,
    session: AsyncSession,
    user: User,
) -> None:
    id_item = query.data.split(":")[0]
    data = await state.get_data()
    if len(data["id_chosen_items"]) == 2 and id_item not in data["id_chosen_items"]:
        await query.answer(
            text=await get_text_message("max_two_items"), show_alert=True
        )
        return
    item: Item = await session.scalar(select(Item).where(Item.id_item == id_item))
    count_props = len(json.loads(item.properties))
    if count_props > prop_quantity_by_rarity["mythical"]:
        await query.answer(
            text=await get_text_message("too_many_props"), show_alert=True
        )
        return
    if id_item in data["id_chosen_items"]:
        data["id_chosen_items"].remove(id_item)
        data["status_chosen_items"].remove(item.is_active)
        data["q_props_items"].remove(count_props)
        data["lvl_items"].remove(item.lvl)
        data["ft_props"].remove(await ft_item_props(item_props=item.properties))
    else:
        data["id_chosen_items"].append(id_item)
        data["status_chosen_items"].append(item.is_active)
        data["q_props_items"].append(count_props)
        data["lvl_items"].append(item.lvl)
        data["ft_props"].append(await ft_item_props(item_props=item.properties))
    await state.update_data(
        id_chosen_items=data["id_chosen_items"],
        status_chosen_items=data["status_chosen_items"],
        q_props_items=data["q_props_items"],
        lvl_items=data["lvl_items"],
        ft_props=data["ft_props"],
    )
    USD_TO_MERGE_ITEMS = 0
    t1 = data["ft_props"][0] if len(data["ft_props"]) > 0 else ""
    t2 = data["ft_props"][1] if len(data["ft_props"]) == 2 else ""
    if len(data["id_chosen_items"]) == 2:
        USD_TO_MERGE_ITEMS = await get_value(
            session=session, value_name="USD_TO_MERGE_ITEMS"
        )
        q_props = sum(data["q_props_items"])
        lvl_sum = sum(data["lvl_items"])
        lvl_sum = 1 if lvl_sum == 0 else lvl_sum
        main_k = q_props + lvl_sum
        USD_TO_MERGE_ITEMS = USD_TO_MERGE_ITEMS * main_k
        await state.update_data(USD_TO_MERGE_ITEMS=USD_TO_MERGE_ITEMS)
    await query.message.edit_text(
        text=await get_text_message(
            "chosen_items_to_merge",
            t1=t1,
            t2=t2,
            utmi=USD_TO_MERGE_ITEMS,
        ),
        reply_markup=await ik_menu_items_for_merge(
            session=session,
            id_user=user.id_user,
            id_chosen_items=data["id_chosen_items"],
            page=data["page"],
        ),
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "merge_items")
async def fi_merge_items(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    USD_TO_MERGE_ITEMS = (await state.get_data())["USD_TO_MERGE_ITEMS"]
    if user.usd < USD_TO_MERGE_ITEMS:
        await query.answer(
            text=await get_text_message("not_enough_usd"), show_alert=True
        )
        return
    user.usd -= USD_TO_MERGE_ITEMS
    user.amount_expenses_usd += USD_TO_MERGE_ITEMS
    data = await state.get_data()
    new_item = await merge_items(
        session=session,
        id_item_1=data["id_chosen_items"][0],
        id_item_2=data["id_chosen_items"][1],
    )
    new_item.id_user = user.id_user
    session.add(new_item)
    await session.commit()
    if any(data["status_chosen_items"]):
        items = await session.scalars(
            select(Item).where(
                and_(Item.id_user == user.id_user, Item.is_active == True)  # noqa: E712
            )
        )
        user.info_about_items = await synchronize_info_about_items(items=list(items))
        await session.commit()
    t = await ft_item_props(item_props=new_item.properties)
    await query.message.edit_text(
        text=await get_text_message(
            "items_merged", name_=new_item.name_with_emoji, t=t
        ),
        reply_markup=await ik_choice_items_to_merge(),
    )
