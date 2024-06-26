from aiogram.types import (
    Message,
    CallbackQuery,
    FSInputFile,
    InputMediaPhoto,
    InputFile,
)
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Animal, Value
from tools import (
    get_text_message,
    disable_not_main_window,
    get_remain_seats,
    get_price_animal,
    get_income_animal,
    add_animal,
    get_total_number_animals,
    get_photo,
    get_dict_animals,
    find_integers
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    rk_back,
    ik_choice_animal_rshop,
    ik_choice_rarity_rshop,
    ik_choice_quantity_animals_rshop,
)
from bot.filters import GetTextButton, CompareDataByIndex
from game_variables import rarities

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.zoomarket_menu, GetTextButton("rarity_shop"), flags=flags)
async def rarity_shop_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    await disable_not_main_window(message=message, data=data)
    msg = await message.answer(
        text=await get_text_message("rarity_shop_menu"),
        reply_markup=await ik_choice_animal_rshop(session=session),
    )
    await state.set_data({})
    await state.update_data(active_window=msg.message_id)


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("rshop_choice_animal")
)
async def get_animal_rshop(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    animal = query.data.split(":")[0]
    await state.update_data(animal=animal)
    await query.message.edit_text(
        text=await get_text_message("choice_rarity_shop_menu"),
        reply_markup=await ik_choice_rarity_rshop(),
    )


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("rshop_choice_rarity")
)
async def get_rarity_rshop(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    rarity = query.data.split(":")[0]
    unity_idpk = int(user.current_unity.split(":")[-1]) if user.current_unity else None
    animal_price = await get_price_animal(
        session=session, animal_code_name=data["animal"] + rarity, unity_idpk=unity_idpk
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == data["animal"] + rarity)
    )
    await state.update_data(
        animal_price=animal_price,
        animal=data["animal"],
        rarity=rarity,
        unity_idpk=unity_idpk,
    )
    animal_income = await get_income_animal(
        session=session, animal=animal, unity_idpk=unity_idpk, items=user.items
    )
    await query.message.delete()
    photo = FSInputFile(f"src_photos/{data.get('animal')}/{animal.code_name}.jpg")
    msg = await query.message.answer_photo(
        photo=photo,
        caption=await get_text_message(
            "choice_quantity_rarity_shop_menu",
            name_=animal.name,
            description=animal.description,
            price=animal_price,
            income=animal_income,
            usd=user.usd,
            quantity_animals=(await get_dict_animals(user)).get(animal.code_name, 0),
        ),
        reply_markup=await ik_choice_quantity_animals_rshop(
            session=session, animal_price=animal_price
        ),
        protect_content=True,
    )
    await state.update_data(active_window=msg.message_id)


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("rshop_switch_rarity")
)
async def rshop_switch_rarity(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    switch_to = query.data.split(":")[0]
    if switch_to == "next_rarity":
        rarity = (
            rarities[rarities.index(data["rarity"]) + 1]
            if data["rarity"] != rarities[-1]
            else rarities[0]
        )
    elif switch_to == "prev_rarity":
        rarity = (
            rarities[rarities.index(data["rarity"]) - 1]
            if data["rarity"] != rarities[0]
            else rarities[-1]
        )
    animal_price = await get_price_animal(
        session=session,
        animal_code_name=data["animal"] + rarity,
        unity_idpk=data["unity_idpk"],
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == data["animal"] + rarity)
    )
    await state.update_data(rarity=rarity, animal_price=animal_price)
    animal_income = await get_income_animal(
        session=session, animal=animal, unity_idpk=data["unity_idpk"], items=user.items
    )
    photo = FSInputFile(f"src_photos/{data.get('animal')}/{animal.code_name}.jpg")
    await query.message.edit_media(
        media=InputMediaPhoto(
            media=photo,
            caption=await get_text_message(
                "choice_quantity_rarity_shop_menu",
                name_=animal.name,
                description=animal.description,
                price=animal_price,
                income=animal_income,
                usd=user.usd,
                quantity_animals=(await get_dict_animals(user)).get(animal.code_name, 0)
            ),
        ),
        reply_markup=await ik_choice_quantity_animals_rshop(
            session=session, animal_price=animal_price
        ),
        protect_content=True,
    )


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("back_rshop"))
async def back_to_rarity_shop_menu(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_choice_animal":
            return await query.message.edit_text(
                text=await get_text_message("rarity_shop_menu"),
                reply_markup=await ik_choice_animal_rshop(session=session),
            )
        case "to_choice_rarity":
            await query.message.delete()
            msg = await query.message.answer(
                text=await get_text_message("choice_rarity_shop_menu"),
                reply_markup=await ik_choice_rarity_rshop(),
            )
            await state.update_data(active_window=msg.message_id)


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("rshop_choice_quantity")
)
async def get_quantity_rshop(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    quantity_animal = int(query.data.split(":")[0])
    remain_seats = await get_remain_seats(
        session=session,
        user=user
    )
    if remain_seats < quantity_animal:
        await query.answer(await get_text_message("not_enough_seats"), show_alert=True)
        return
    data = await state.get_data()
    finite_price = data["animal_price"] * quantity_animal
    if user.usd < finite_price:
        return await query.answer(
            text=await get_text_message("not_enough_money"),
            show_alert=True,
        )
    user.usd -= finite_price
    user.amount_expenses_usd += finite_price
    await add_animal(
        self=user,
        code_name_animal=data["animal"] + data["rarity"],
        quantity=quantity_animal,
    )
    await query.answer(
        await get_text_message("offer_bought_successfully"), show_alert=True
    )
    await session.commit()
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == data["animal"] + data["rarity"])
    )
    await query.message.edit_caption(
        caption=await get_text_message(
            "choice_quantity_rarity_shop_menu",
            name_=animal.name,
            description=animal.description,
            price=data["animal_price"],
            income=await get_income_animal(
                session=session,
                animal=animal,
                unity_idpk=data["unity_idpk"],
                items=user.items,
            ),
            usd=user.usd,
            quantity_animals=(await get_dict_animals(user)).get(animal.code_name, 0)
        ),
        reply_markup=await ik_choice_quantity_animals_rshop(
            session=session, animal_price=data["animal_price"]
        ),
        protect_content=True,
    )


@router.callback_query(UserState.zoomarket_menu, F.data == "cqa_rshop")
async def custom_quantity_animals_rshop(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.message.delete_reply_markup()
    data = await state.get_data()
    animals_are_available = user.usd // data["animal_price"]
    await query.message.answer(
        text=await get_text_message(
            "enter_custom_quantity_animals", available=animals_are_available
        ),
        reply_markup=await rk_back(),
    )
    await state.set_state(UserState.rshop_enter_custom_qa_step)


@router.message(UserState.rshop_enter_custom_qa_step, GetTextButton("back"))
async def back_to_choice_quantity_rshop(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    await message.answer(
        text=await get_text_message("backed"), reply_markup=await rk_zoomarket_menu()
    )
    animal = await session.scalar(
        select(Animal).where(Animal.code_name == data["animal"] + data["rarity"])
    )
    unity_idpk = int(user.current_unity.split(":")[-1]) if user.current_unity else None
    animal_income = await get_income_animal(
        session=session, animal=animal, unity_idpk=unity_idpk, items=user.items
    )
    photo = FSInputFile(f"src_photos/{data.get('animal')}/{animal.code_name}.jpg")
    msg = await message.answer_photo(
        photo=photo,
        caption=await get_text_message(
            "choice_quantity_rarity_shop_menu",
            name_=animal.name,
            description=animal.description,
            price=data["animal_price"],
            income=animal_income,
            usd=user.usd,
            quantity_animals=(await get_dict_animals(user)).get(animal.code_name, 0)
        ),
        reply_markup=await ik_choice_quantity_animals_rshop(
            session=session, animal_price=data["animal_price"]
        ),
    )
    await state.update_data(active_window=msg.message_id)
    await state.set_state(UserState.zoomarket_menu)


@router.message(UserState.rshop_enter_custom_qa_step)
async def get_custom_quantity_animals_rshop(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    quantity_animal = await find_integers(message.text)
    if not quantity_animal:
        await message.answer(text=await get_text_message("enter_digit"))
        return
    if quantity_animal < 1:
        await message.answer(text=await get_text_message("enter_digit"))
        return
    remain_seats = await get_remain_seats(
        session=session,
        user=user
    )
    if remain_seats < quantity_animal:
        await message.answer(await get_text_message("not_enough_seats"))
        return
    data = await state.get_data()
    finite_price = quantity_animal * data["animal_price"]
    if user.usd < finite_price:
        await message.answer(text=await get_text_message("not_enough_money"))
        return
    user.usd -= finite_price
    user.amount_expenses_usd += finite_price
    await add_animal(
        self=user,
        code_name_animal=data["animal"] + data["rarity"],
        quantity=quantity_animal,
    )
    await message.answer(
        text=await get_text_message("you_paid", fp=finite_price),
        reply_markup=await rk_zoomarket_menu(),
    )
    await session.commit()
    await state.set_state(UserState.zoomarket_menu)
