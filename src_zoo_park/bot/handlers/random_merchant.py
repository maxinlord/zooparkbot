from aiogram.types import Message, CallbackQuery, ReplyKeyboardRemove, ReactionTypeEmoji
from aiogram import F, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from db import User, Photo, RandomMerchant, Animal, Value
from aiogram.utils.chat_action import ChatActionSender
from tools import (
    get_text_message,
    create_random_merchant,
    gen_quantity_animals,
    gen_price,
    get_random_animal,
    get_animal_with_random_rarity,
    disable_not_main_window,
    get_remain_seats,
    add_animal,
    get_total_number_animals
)
from bot.states import UserState
from bot.keyboards import (
    rk_zoomarket_menu,
    ik_merchant_menu,
    ik_choice_animal_rmerchant,
    ik_choice_quantity_animals_rmerchant,
    rk_back,
)
from bot.filters import GetTextButton, CompareDataByIndex
import random
import asyncio

flags = {"throttling_key": "default"}
router = Router()


@router.message(UserState.zoomarket_menu, GetTextButton("random_merchant"), flags=flags)
async def random_merchant_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await disable_not_main_window(data=await state.get_data(), message=message)
    merchant: RandomMerchant = await session.scalar(
        select(RandomMerchant).where(RandomMerchant.id_user == user.id_user)
    )
    if not merchant:
        merchant: RandomMerchant = await create_random_merchant(id_user=user.id_user)
    animal_name = await session.scalar(
        select(Animal.name).where(Animal.code_name == merchant.code_name_animal)
    )
    msg = await message.answer_photo(
        photo=await session.scalar(
            select(Photo.photo_id).where(Photo.name == "plug_photo")
        ),
        caption=await get_text_message("random_merchant_menu", n=merchant.name),
        reply_markup=await ik_merchant_menu(
            quantity_animals=merchant.quantity_animals,
            name_animal=animal_name,
            discount=merchant.discount,
            price_with_discount=merchant.price_with_discount,
            price=merchant.price,
            first_offer_bought=merchant.first_offer_bought,
        ),
    )
    await state.set_data({})
    await state.update_data(active_window=msg.message_id, animal_name=animal_name)


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("offer"))
async def buy_one_of_offer(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    offer = query.data.split(":")[0]
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
            remain_seats = await get_remain_seats(
                aviaries=user.aviaries, amount_animals=await get_total_number_animals(self=user)
            )
            if remain_seats < merchant.quantity_animals:
                await query.answer(
                    await get_text_message("not_enough_seats"), show_alert=True
                )
                return
            await add_animal(
                self=user,
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
            remain_seats = await get_remain_seats(
                aviaries=user.aviaries, amount_animals=await get_total_number_animals(self=user)
            )
            MAX_QUANTITY_ANIMALS = await session.scalar(
                select(Value.value_int).where(Value.name == "MAX_QUANTITY_ANIMALS")
            )
            if remain_seats < MAX_QUANTITY_ANIMALS:
                await query.answer(
                    await get_text_message("no_seats_to_full_prize"), show_alert=True
                )
                return
            await query.message.delete_reply_markup()
            user.usd -= merchant.price
            user.amount_expenses_usd += merchant.price
            quantity_animals = await gen_quantity_animals()

            await state.set_state(UserState.for_while_shell)
            while quantity_animals > 0:
                animal = await get_random_animal(session=session, user_animals=user.animals)
                part_animals = random.randint(1, quantity_animals)
                quantity_animals -= part_animals
                await add_animal(
                    self=user,
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
            await state.set_state(UserState.zoomarket_menu)

            await query.message.answer(await get_text_message("you_lucky"))
            merchant.price = await gen_price()
            await session.commit()

        case "3":
            await query.message.edit_caption(
                caption=await get_text_message("merchant_choice_animal"),
                reply_markup=await ik_choice_animal_rmerchant(),
            )


@router.callback_query(
    UserState.zoomarket_menu,
    CompareDataByIndex("choice_animal_rmerchant"),
)
async def choice_animal_to_buy(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    animal = query.data.split(":")[0]
    animal_price = await session.scalar(
        select(Animal.price).where(Animal.code_name == f"{animal}-")
    )
    await state.update_data(code_name_animal=animal, animal_price=animal_price)
    await query.message.edit_caption(
        caption=await get_text_message("merchant_choise_quantity_animal"),
        reply_markup=await ik_choice_quantity_animals_rmerchant(
            animal_price=animal_price
        ),
    )


@router.callback_query(
    UserState.zoomarket_menu, CompareDataByIndex("choice_qa_rmerchant")
)
async def choice_qa_to_buy(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    animal: str = data["code_name_animal"]
    animal_price = data["animal_price"]
    quantity = int(query.data.split(":")[0])
    finite_price = animal_price * quantity

    remain_seats = await get_remain_seats(
        aviaries=user.aviaries, amount_animals=await get_total_number_animals(self=user)
    )
    if remain_seats < quantity:
        await query.answer(await get_text_message("not_enough_seats"), show_alert=True)
        return
    if user.usd < finite_price:
        await query.answer(await get_text_message("not_enough_money"), show_alert=True)
        return
    user.usd -= finite_price
    user.amount_expenses_usd += finite_price
    await query.message.delete_reply_markup()

    await state.set_state(UserState.for_while_shell)
    while quantity > 0:
        animal_obj: Animal = await get_animal_with_random_rarity(
            animal=data["code_name_animal"]
        )
        part_animals = random.randint(1, quantity)
        quantity -= part_animals
        async with ChatActionSender.typing(
            bot=query.bot, chat_id=query.message.chat.id
        ):
            await asyncio.sleep(2)
            await query.message.answer(
                await get_text_message(
                    "you_got_this_rarity_animal", an=animal_obj.name, aq=part_animals
                )
            )

        await add_animal(
            self=user,
            code_name_animal=animal_obj.code_name,
            quantity=part_animals,
        )
    await state.set_state(UserState.zoomarket_menu)

    await query.message.answer(text=await get_text_message("you_lucky"))
    await session.commit()


@router.callback_query(UserState.for_while_shell)
async def for_while_shell_callback(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.answer(text=await get_text_message("while_shell"), show_alert=False)


@router.message(UserState.for_while_shell)
async def random_merchant_menu(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await message.react(reaction=[ReactionTypeEmoji(emoji="🗿")])


@router.callback_query(UserState.zoomarket_menu, CompareDataByIndex("back"))
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
            data = await state.get_data()
            animal_name = data["animal_name"]
            await query.message.edit_caption(
                caption=await get_text_message("random_merchant_menu", n=merchant.name),
                reply_markup=await ik_merchant_menu(
                    quantity_animals=merchant.quantity_animals,
                    name_animal=animal_name,
                    discount=merchant.discount,
                    price_with_discount=merchant.price_with_discount,
                    price=merchant.price,
                    first_offer_bought=merchant.first_offer_bought,
                ),
            )
        case "to_choice_animal":
            await query.message.edit_caption(
                caption=await get_text_message("merchant_choise_animal"),
                reply_markup=await ik_choice_animal_rmerchant(),
            )


@router.callback_query(UserState.zoomarket_menu, F.data == "cqa")
async def custom_quantity_animals(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await query.message.delete_reply_markup()
    data = await state.get_data()
    animal_price = data["animal_price"]
    animals_are_available = user.usd // animal_price
    await query.message.answer(
        text=await get_text_message(
            "enter_custom_quantity_animals", available=animals_are_available
        ),
        reply_markup=await rk_back(),
    )
    await state.set_state(UserState.rmerchant_enter_custom_qa_step)


@router.message(UserState.rmerchant_enter_custom_qa_step, GetTextButton("back"))
async def back_to_choice_quantity(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    data = await state.get_data()
    await message.answer(
        text=await get_text_message("backed"), reply_markup=await rk_zoomarket_menu()
    )
    msg = await message.answer_photo(
        photo=await session.scalar(
            select(Photo.photo_id).where(Photo.name == "plug_photo")
        ),
        caption=await get_text_message("merchant_choise_quantity_animal"),
        reply_markup=await ik_choice_quantity_animals_rmerchant(
            animal_price=data["animal_price"]
        ),
    )
    await state.update_data(active_window=msg.message_id)
    await state.set_state(UserState.zoomarket_menu)


@router.message(UserState.rmerchant_enter_custom_qa_step)
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
    remain_seats = await get_remain_seats(
        aviaries=user.aviaries, amount_animals=await get_total_number_animals(self=user)
    )
    if remain_seats < int(message.text):
        await message.answer(
            await get_text_message("not_enough_seats"), show_alert=True
        )
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
    await state.set_state(UserState.for_while_shell)
    while quantity > 0:
        animal = await get_animal_with_random_rarity(animal=data["code_name_animal"])
        part_animals = random.randint(1, quantity)
        quantity -= part_animals
        async with ChatActionSender.typing(bot=message.bot, chat_id=message.chat.id):
            await asyncio.sleep(2)
            await message.answer(
                await get_text_message(
                    "you_got_this_rarity_animal", an=animal.name, aq=part_animals
                )
            )
        await add_animal(
            self=user,
            code_name_animal=animal.code_name,
            quantity=part_animals,
        )
    await state.set_state(UserState.zoomarket_menu)

    await message.answer(
        await get_text_message("you_lucky"), reply_markup=await rk_zoomarket_menu()
    )
    await session.commit()
