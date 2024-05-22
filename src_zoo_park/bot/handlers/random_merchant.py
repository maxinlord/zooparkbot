from datetime import datetime
from aiogram.filters import CommandStart, CommandObject
from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Value, Photo, RandomMerchant, Animal
from aiogram.filters import StateFilter
from aiogram.utils.chat_action import ChatActionSender
from aiogram.fsm.state import default_state
from tools import (
    get_text_message,
    has_special_characters_nickname,
    is_unique_nickname,
    shorten_whitespace_nickname,
    validate_command_arg,
    create_random_merchant,
    calculate_price_with_discount,
    add_animal,
    gen_quantity_animals,
    gen_price,
    get_random_animal,
    get_animal_with_random_rarity,
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    ik_merchant_menu,
    ik_choise_animal,
    ik_choise_quantity_animals,
    rk_back,
)
from bot.filters import GetTextButton
import random
import asyncio

router = Router()


@router.message(GetTextButton("random_merchant"))
async def random_merchant_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    merchant: RandomMerchant = await session.scalar(
        select(RandomMerchant).where(RandomMerchant.id_user == user.id_user)
    )
    if not merchant:
        merchant: RandomMerchant = await create_random_merchant(id_user=user.id_user)
    animal_name = await session.scalar(
        select(Animal.name).where(Animal.code_name == merchant.code_name_animal)
    )
    await message.answer_photo(
        photo=await session.scalar(
            select(Photo.photo_id).where(Photo.name == "plug_photo")
        ),
        caption=await get_text_message("random_merchant_menu"),
        reply_markup=await ik_merchant_menu(
            quantity_animals=merchant.quantity_animals,
            name_animal=animal_name,
            discount=merchant.discount,
            price_with_discount=merchant.price_with_discount,
            price=merchant.price,
            first_offer_bought=merchant.first_offer_bought,
        ),
    )


@router.callback_query(F.data.split("_")[-1] == "offer")
async def buy_one_of_offer(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    offer = query.data.split("_")[0]
    merchant = await session.scalar(
        select(RandomMerchant).where(RandomMerchant.id_user == user.id_user)
    )
    match offer:
        case "1":
            if user.usd < merchant.price_with_discount:
                await query.answer(
                    await get_text_message("not_enough_money"),
                    show_alert=True,
                )
                return
            user.animals = await add_animal(
                user.animals,
                code_name_animal=merchant.code_name_animal,
                quantity=merchant.quantity_animals,
            )
            user.usd -= merchant.price_with_discount
            user.amount_expenses_usd += merchant.price_with_discount
            merchant.first_offer_bought = True
            await session.commit()
            await query.message.edit_reply_markup(
                reply_markup=await ik_merchant_menu(
                    price=merchant.price,
                    first_offer_bought=True,
                )
            )
            await query.answer(
                await get_text_message("offer_bought_successfully"), show_alert=True
            )
        case "2":
            if user.usd < merchant.price:
                await query.answer(
                    await get_text_message("not_enough_money"), show_alert=True
                )
                return
            await query.message.delete_reply_markup()
            user.usd -= merchant.price
            user.amount_expenses_usd += merchant.price
            quantity_animals = await gen_quantity_animals()
            while quantity_animals > 0:
                animal = await get_random_animal()
                part_animals = random.randint(1, quantity_animals)
                quantity_animals -= part_animals
                user.animals = await add_animal(
                    user.animals,
                    code_name_animal=animal.code_name,
                    quantity=part_animals,
                )
                async with ChatActionSender.typing(
                    bot=query.bot, chat_id=query.message.chat.id
                ):
                    await asyncio.sleep(2)
                    await query.message.answer(
                        await get_text_message(
                            "you_got_this_animal", an=animal.name, aq=part_animals
                        )
                    )
            await query.answer(await get_text_message("you_lucky"), show_alert=True)
            merchant.price = await gen_price()
            await session.commit()

        case "3":
            await query.message.edit_caption(
                caption=await get_text_message("merchant_choise_animal"),
                reply_markup=await ik_choise_animal(),
            )


@router.callback_query(F.data.split("_")[-1] == "3offerAnimal")
async def choise_animal_to_buy(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    animal = query.data.split("_")[0]
    animal_price = await session.scalar(
        select(Animal.price).where(Animal.code_name == f"{animal}-")
    )
    await query.message.edit_caption(
        caption=await get_text_message("merchant_choise_quantity_animal"),
        reply_markup=await ik_choise_quantity_animals(
            animal=animal, animal_price=animal_price
        ),
    )


@router.callback_query(F.data.split("_")[-1] == "3offerQuantity")
async def choise_qtity_to_buy(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    animal_str = query.data.split("_")[0]
    animal_price = await session.scalar(
        select(Animal.price).where(Animal.code_name == f"{animal_str}-")
    )
    quantity = int(query.data.split("_")[1])
    finite_price = animal_price * quantity
    if user.usd < finite_price:
        await query.answer(await get_text_message("not_enough_money"), show_alert=True)
        return
    user.usd -= finite_price
    user.amount_expenses_usd += finite_price
    await query.message.delete_reply_markup()
    await query.answer(cache_time=1)
    while quantity > 0:
        animal = await get_animal_with_random_rarity(animal=animal_str)
        part_animals = random.randint(1, quantity)
        quantity -= part_animals
        user.animals = await add_animal(
            user.animals,
            code_name_animal=animal.code_name,
            quantity=part_animals,
        )
        async with ChatActionSender.typing(
            bot=query.bot, chat_id=query.message.chat.id
        ):
            await asyncio.sleep(2)
            await query.message.answer(
                await get_text_message(
                    "you_got_this_rarity_animal", an=animal.name, aq=part_animals
                )
            )
    await query.answer(text=await get_text_message("you_lucky"), show_alert=True)
    await session.commit()


@router.callback_query(F.data.split(":")[-1] == "back")
async def back_distributor(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    back_to = query.data.split(":")[0]
    match back_to:
        case "to_all_offers":
            merchant = await session.scalar(
                select(RandomMerchant).where(RandomMerchant.id_user == user.id_user)
            )
            animal_name = await session.scalar(
                select(Animal.name).where(Animal.code_name == merchant.code_name_animal)
            )
            await query.message.edit_caption(
                caption=await get_text_message("random_merchant_menu"),
                reply_markup=await ik_merchant_menu(
                    quantity_animals=merchant.quantity_animals,
                    name_animal=animal_name,
                    discount=merchant.discount,
                    price_with_discount=merchant.price_with_discount,
                    price=merchant.price,
                    first_offer_bought=merchant.first_offer_bought,
                ),
            )
        case "to_choise_animal":
            await query.message.edit_caption(
                caption=await get_text_message("merchant_choise_animal"),
                reply_markup=await ik_choise_animal(),
            )


@router.callback_query(F.data.split(":")[-1] == "cqa")
async def custom_quantity_animals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.message.delete_reply_markup()
    animal_str = query.data.split(":")[0]
    animal_price = await session.scalar(
        select(Animal.price).where(Animal.code_name == f"{animal_str}-")
    )
    animals_are_available = user.usd // animal_price
    await query.message.answer(
        text=await get_text_message(
            "enter_custom_quantity_animals", available=animals_are_available
        ),
        reply_markup=await rk_back(),
    )
    await state.set_state(UserState.enter_custom_quantity_animals)
    await state.update_data(animal_str=animal_str, animal_price=animal_price)


@router.message(UserState.enter_custom_quantity_animals, GetTextButton("back"))
async def back_to_choise_quantity(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    await message.answer(
        text=await get_text_message("backed"), reply_markup=await rk_zoomarket_menu()
    )
    await message.answer_photo(
        photo=await session.scalar(
            select(Photo.photo_id).where(Photo.name == "plug_photo")
        ),
        caption=await get_text_message("merchant_choise_quantity_animal"),
        reply_markup=await ik_choise_quantity_animals(
            animal_price=data["animal_price"], animal=data["animal_str"]
        ),
    )
    await state.clear()


@router.message(UserState.enter_custom_quantity_animals)
async def get_custom_quantity_animals(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    if not message.text.isdigit():
        await message.answer(text=await get_text_message("enter_digit"))
        return
    if int(message.text) < 1:
        await message.answer(text=await get_text_message("enter_digit"))
        return
    data = await state.get_data()
    finite_price = int(message.text) * data["animal_price"]
    if user.usd < finite_price:
        await message.answer(text=await get_text_message("not_enough_money"))
        return
    user.usd -= finite_price
    user.amount_expenses_usd += finite_price
    quantity = int(message.text)
    await message.answer(
        text=await get_text_message("you_paid", fp=finite_price),
        reply_markup=ReplyKeyboardRemove(),
    )
    while quantity > 0:
        animal = await get_animal_with_random_rarity(animal=data["animal_str"])
        part_animals = random.randint(1, quantity)
        quantity -= part_animals
        async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
            await asyncio.sleep(2)
            await message.answer(
                await get_text_message(
                    "you_got_this_rarity_animal", an=animal.name, aq=part_animals
                )
            )
        user.animals = await add_animal(
            user.animals,
            code_name_animal=animal.code_name,
            quantity=part_animals,
        )
    await message.answer(
        await get_text_message("you_lucky"), reply_markup=await rk_zoomarket_menu()
    )
    await session.commit()
