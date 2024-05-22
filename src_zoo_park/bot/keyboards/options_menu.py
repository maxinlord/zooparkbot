from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from tools import get_text_button, get_all_animals, get_all_quantity_animals


async def ik_merchant_menu(
    price: int,
    first_offer_bought: bool,
    quantity_animals: int = None,
    name_animal: str = None,
    discount: int = None,
    price_with_discount: int = None,
):
    builder = InlineKeyboardBuilder()
    if not first_offer_bought:
        builder.button(
            text=await get_text_button(
                "first_offer",
                qa=quantity_animals,
                na=name_animal,
                d1=discount,
                pd1=price_with_discount,
            ),
            callback_data="1_offer",
        )
    builder.button(
        text=await get_text_button("second_offer", p=price),
        callback_data="2_offer",
    )
    builder.button(text=await get_text_button("third_offer"), callback_data="3_offer")
    builder.adjust(1)
    return builder.as_markup()


async def ik_choise_animal():
    builder = InlineKeyboardBuilder()
    all_animals = await get_all_animals()
    for animal in all_animals:
        builder.button(text=animal.name, callback_data=f"{animal.code_name.strip('-')}_3offerAnimal")
    builder.button(
        text=await get_text_button("back"), callback_data="to_all_offers:back"
    )
    quantity_names = len(all_animals)
    if quantity_names >= 3:
        adjust = [3 for _ in range(quantity_names // 3)]
        remains = quantity_names % 3
        adjust = adjust + [remains] if remains > 0 else adjust
    else:
        adjust = [quantity_names]
    builder.adjust(*adjust, 1)
    return builder.as_markup()


async def ik_choise_quantity_animals(animal: str, animal_price: int):
    builder = InlineKeyboardBuilder()
    all_quantity_animals = await get_all_quantity_animals()
    prices = [animal_price * q for q in all_quantity_animals]
    for quantity_animal, price in zip(all_quantity_animals, prices):
        builder.button(
            text=await get_text_button("pattern_quantity_animals", qa=quantity_animal, pr=price),
            callback_data=f"{animal}_{quantity_animal}_3offerQuantity",
        )
    builder.button(
        text=await get_text_button("custom_quantity_animals"),
        callback_data=f"{animal}:cqa", #custom_quantity_animals
    )
    builder.button(
        text=await get_text_button("back"), callback_data="to_choise_animal:back"
    )
    builder.adjust(1)
    return builder.as_markup()
