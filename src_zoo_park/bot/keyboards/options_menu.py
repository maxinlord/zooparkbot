from aiogram.utils.keyboard import InlineKeyboardBuilder, ReplyKeyboardBuilder
from aiogram.types import SwitchInlineQueryChosenChat
from tools import (
    get_text_button,
    get_all_animals,
    get_quantity_animals_for_rmerchant,
    get_quantity_animals_for_rshop,
    get_all_name_items,
    get_all_name_aviaries,
    get_quantity_animals_for_avi,
    get_row_items_for_kb,
    get_size_items_for_kb,
    get_items_data_to_kb,
    get_size_unity_for_kb,
    get_row_unity_for_kb,
    get_unity_name_and_idpk,
    get_size_unity_members,
    get_row_unity_members,
    get_members_name_and_idpk,
)
from config import rarities, colors_rarities
from itertools import islice


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
                dnt=discount,
                pwd=price_with_discount,
            ),
            callback_data="1:offer",
        )
    builder.button(
        text=await get_text_button("second_offer", p=price),
        callback_data="2:offer",
    )
    builder.button(text=await get_text_button("third_offer"), callback_data="3:offer")
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_animal_rmerchant():
    builder = InlineKeyboardBuilder()
    all_animals = await get_all_animals()
    for animal in all_animals:
        builder.button(
            text=animal.name,
            callback_data=f"{animal.code_name.strip('-')}:choice_animal_rmerchant",
        )
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


async def ik_choice_quantity_animals_rmerchant(animal_price: int):
    builder = InlineKeyboardBuilder()
    all_quantity_animals = await get_quantity_animals_for_rmerchant()
    prices = [animal_price * q for q in all_quantity_animals]
    for quantity_animal, price in zip(all_quantity_animals, prices):
        builder.button(
            text=await get_text_button(
                "pattern_quantity_animals", qa=quantity_animal, pr=price
            ),
            callback_data=f"{quantity_animal}:choice_qa_rmerchant",
        )
    builder.button(
        text=await get_text_button("custom_quantity_animals"),
        callback_data="cqa",  # custom_quantity_animals
    )
    builder.button(
        text=await get_text_button("back"), callback_data="to_choice_animal:back"
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_animal_rshop():
    builder = InlineKeyboardBuilder()
    all_animals = await get_all_animals()
    for animal in all_animals:
        builder.button(
            text=animal.name,
            callback_data=f"{animal.code_name.strip('-')}:rshop_choice_animal",
        )
    builder.adjust(2)
    return builder.as_markup()


async def ik_choice_rarity_rshop():
    builder = InlineKeyboardBuilder()
    for rarity, color_rarity in zip(rarities, colors_rarities):
        builder.button(text=color_rarity, callback_data=f"{rarity}:rshop_choice_rarity")
    builder.button(
        text=await get_text_button("back"), callback_data="to_choice_animal:back_rshop"
    )
    builder.adjust(4, 1)
    return builder.as_markup()


async def ik_choice_quantity_animals_rshop(animal_price: int):
    builder = InlineKeyboardBuilder()
    all_quantity_animals = await get_quantity_animals_for_rshop()
    prices = [animal_price * q for q in all_quantity_animals]
    for quantity_animal, price in zip(all_quantity_animals, prices):
        builder.button(
            text=await get_text_button(
                "pattern_quantity_animals_rshop", qa=quantity_animal, pr=price
            ),
            callback_data=f"{quantity_animal}:rshop_choice_quantity",
        )
    builder.button(
        text=await get_text_button("custom_quantity_animals"),
        callback_data="cqa_rshop",
    )
    builder.button(
        text=await get_text_button("back"),
        callback_data="to_choice_rarity:back_rshop",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_item():
    builder = InlineKeyboardBuilder()
    all_items = await get_all_name_items()
    for name, code_name in all_items:
        builder.button(text=name, callback_data=f"{code_name}:choice_item_witems")
    builder.adjust(1)
    return builder.as_markup()


async def ik_buy_item(bought: bool):
    builder = InlineKeyboardBuilder()
    if not bought:
        builder.button(text=await get_text_button("buy_item"), callback_data="buy_item")
    builder.button(
        text=await get_text_button("back"), callback_data="to_witems_menu:back_witems"
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_item():
    builder = InlineKeyboardBuilder()
    all_items = await get_all_name_items()
    for name, code_name in all_items:
        builder.button(text=name, callback_data=f"{code_name}:choice_item_witems")
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_aviary():
    builder = InlineKeyboardBuilder()
    all_aviaries = await get_all_name_aviaries()
    for name, code_name in all_aviaries:
        builder.button(text=name, callback_data=f"{code_name}:choice_aviary_aviaries")
    builder.adjust(1)
    return builder.as_markup()


async def ik_choice_quantity_aviary_avi(aviary_price: int):
    builder = InlineKeyboardBuilder()
    all_quantity_aviaries = await get_quantity_animals_for_avi()
    prices = [aviary_price * q for q in all_quantity_aviaries]
    for quantity_aviary, price in zip(all_quantity_aviaries, prices):
        builder.button(
            text=await get_text_button(
                "pattern_quantity_aviary_avi", qa=quantity_aviary, pr=price
            ),
            callback_data=f"{quantity_aviary}:choice_quantity_avi",
        )
    builder.button(
        text=await get_text_button("custom_quantity_aviary"),
        callback_data="cqa_avi",
    )
    builder.button(
        text=await get_text_button("back"),
        callback_data="to_choice_aviary:back_avi",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_bank():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("exchange"), callback_data="exchange_bank"
    )
    builder.button(text=await get_text_button("update"), callback_data="update_bank")
    builder.adjust(1)
    return builder.as_markup()


async def rk_exchange_bank():
    builder = ReplyKeyboardBuilder()
    builder.button(text=await get_text_button("exchange_all_amount"))
    builder.button(text=await get_text_button("back"))
    builder.adjust(1)
    return builder.as_markup(resize_keyboard=True)


async def ik_account_menu():
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button("items"), callback_data="items")
    builder.button(
        text=await get_text_button("referrals_system"), callback_data="referrals_system"
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_menu_items(QUANTITY_ONE_PAGE_ITEMS: int, current_page: int = 1):
    builder = InlineKeyboardBuilder()
    all_name_items = await get_all_name_items()
    builder.adjust(1)
    return builder.as_markup()


async def ik_menu_items(
    items: str, row_keyboard: int = None, page: int = 1, size_items: int = None
) -> InlineKeyboardBuilder:
    row_keyboard = row_keyboard or await get_row_items_for_kb()
    size_items = size_items or await get_size_items_for_kb()
    builder = InlineKeyboardBuilder()
    start = (page - 1) * size_items
    stop = start + size_items
    items_data = await get_items_data_to_kb(items=items)
    sliced_items_name = islice(items_data, start, stop)
    count_items = 0
    for name, code_name, emoji in sliced_items_name:
        builder.button(
            text=await get_text_button(
                name="pattern_button_name_item", n=name, ej=emoji
            ),
            callback_data=f"{code_name}:tap_item",
        )
        count_items += 1

    whole_pairs = count_items // row_keyboard
    remainder = count_items % row_keyboard
    row = (
        [row_keyboard for _ in range(whole_pairs)] + [remainder]
        if remainder
        else [row_keyboard for _ in range(whole_pairs)]
    )

    builder.button(
        text=await get_text_button("arrow_left"),
        callback_data="left",
    )
    builder.button(text=await get_text_button("arrow_right"), callback_data="right")
    builder.button(
        text=await get_text_button("back"), callback_data="to_account:back_account"
    )
    builder.adjust(*row, 2, 1)

    return builder.as_markup()


async def ik_item_activate_menu(is_activate: bool):
    builder = InlineKeyboardBuilder()
    match is_activate:
        case True:
            builder.button(
                text=await get_text_button("item_deactivate"),
                callback_data="item_deactivate",
            )
        case False:
            builder.button(
                text=await get_text_button("item_activate"),
                callback_data="item_activate",
            )
    builder.button(
        text=await get_text_button("back"), callback_data="to_items:back_account"
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_unity_options():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("create_unity"), callback_data="create_unity"
    )
    builder.button(
        text=await get_text_button("join_to_unity"), callback_data="join_to_unity"
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_update_level_unity():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("update_level_unity"),
        callback_data="update_level_unity",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_menu_unity_to_join(
    row_keyboard: int = None, page: int = 1, size: int = None
) -> InlineKeyboardBuilder:
    row_keyboard = row_keyboard or await get_row_unity_for_kb()
    size = size or await get_size_unity_for_kb()
    builder = InlineKeyboardBuilder()
    start = (page - 1) * size
    stop = start + size
    data = await get_unity_name_and_idpk()
    slice = islice(data, start, stop)
    counter = 0
    for name, idpk_owner in slice:
        builder.button(
            text=await get_text_button(
                name="pattern_button_name_unity",
                n=name,
            ),
            callback_data=f"{idpk_owner}:tap_unity",
        )
        counter += 1
    whole_pairs = counter // row_keyboard
    remainder = counter % row_keyboard
    row = (
        [row_keyboard for _ in range(whole_pairs)] + [remainder]
        if remainder
        else [row_keyboard for _ in range(whole_pairs)]
    )

    builder.button(
        text=await get_text_button("arrow_left"),
        callback_data="left:unity",
    )
    builder.button(
        text=await get_text_button("arrow_right"), callback_data="right:unity"
    )
    builder.button(
        text=await get_text_button("back"), callback_data="to_menu_unity:back_unity"
    )
    builder.adjust(*row, 2, 1)

    return builder.as_markup()


async def ik_unity_send_request():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("send_a_request"),
        callback_data="request_unity",
    )
    builder.button(
        text=await get_text_button("back"),
        callback_data="to_all_unity:back_unity",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_unity_invitation(idpk_user: int | str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("accept_to_unity"),
        callback_data=f"{idpk_user}:accept_to_unity",
    )
    builder.button(
        text=await get_text_button("rejected_to_unity"),
        callback_data=f"{idpk_user}:rejected_to_unity",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_menu_unity_members(
    unity_idpk: int,
    row_keyboard: int = None,
    page: int = 1,
    size: int = None,
) -> InlineKeyboardBuilder:
    row_keyboard = row_keyboard or await get_row_unity_members()
    size = size or await get_size_unity_members()
    builder = InlineKeyboardBuilder()
    start = (page - 1) * size
    stop = start + size
    data = await get_members_name_and_idpk(idpk_unity=unity_idpk)
    slice = islice(data, start, stop)
    counter = 0
    for name, idpk in slice:
        builder.button(
            text=await get_text_button(
                name="pattern_name_unity_member",
                n=name,
            ),
            callback_data=f"{idpk}:tap_member",
        )
        counter += 1
    whole_pairs = counter // row_keyboard
    remainder = counter % row_keyboard
    row = (
        [row_keyboard for _ in range(whole_pairs)] + [remainder]
        if remainder
        else [row_keyboard for _ in range(whole_pairs)]
    )

    builder.button(
        text=await get_text_button("arrow_left"),
        callback_data="left:unity_member",
    )
    builder.button(
        text=await get_text_button("arrow_right"), callback_data="right:unity_member"
    )
    builder.adjust(*row, 2, 1)

    return builder.as_markup()


async def ik_member_menu():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("delete_from_members"),
        callback_data="delete_from_members",
    )
    builder.button(
        text=await get_text_button("back"),
        callback_data="to_all_members:back_unity_members",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_back_member():
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("back"),
        callback_data="to_all_members:back_unity_members",
    )
    return builder.as_markup()


async def ik_get_bonus(sub_on_chat: bool, sub_on_channel: bool):
    builder = InlineKeyboardBuilder()
    if not sub_on_chat:
        builder.button(
            text=await get_text_button("get_bonus_chat"), callback_data="get_bonus_chat"
        )
    if not sub_on_channel:
        builder.button(
            text=await get_text_button("get_bonus_channel"),
            callback_data="get_bonus_channel",
        )
    builder.button(text=await get_text_button("get_bonus"), callback_data="get_bonus")
    builder.adjust(1)
    return builder.as_markup()


async def ik_referrals_menu(promo_text: str):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("share_link"),
        switch_inline_query=promo_text,
    )
    builder.button(text=await get_text_button("back"), callback_data="back_ref")
    builder.adjust(1)
    return builder.as_markup()


async def ik_get_money(one_piece: int, remain_pieces: int, idpk_tr: int):
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button(
            "get_money", remain_pieces=remain_pieces, one_piece=one_piece
        ),
        callback_data=f"{idpk_tr}:activate_tr",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_get_money_one_piece(idpk_tr: int):
    builder = InlineKeyboardBuilder()
    builder = InlineKeyboardBuilder()
    builder.button(
        text=await get_text_button("get_money_one_piece"),
        callback_data=f"{idpk_tr}:activate_tr",
    )
    builder.adjust(1)
    return builder.as_markup()


async def ik_button_play(game_type: str, total_moves: int, remain_moves: int):
    builder = InlineKeyboardBuilder()
    match game_type:
        case "🎯":
            builder.button(
                text=await get_text_button(
                    "dart",
                    total_moves=total_moves,
                    remain_moves=remain_moves,
                ),
                callback_data="dice",
            )
        case "🎳":
            builder.button(
                text=await get_text_button(
                    "bowling",
                    total_moves=total_moves,
                    remain_moves=remain_moves,
                ),
                callback_data="dice",
            )
        case "🎲":
            builder.button(
                text=await get_text_button(
                    "dice",
                    total_moves=total_moves,
                    remain_moves=remain_moves,
                ),
                callback_data="dice",
            )
        case "⚽️":
            builder.button(
                text=await get_text_button(
                    "football",
                    total_moves=total_moves,
                    remain_moves=remain_moves,
                ),
                callback_data="dice",
            )
        case "🏀":
            builder.button(
                text=await get_text_button(
                    "basketball",
                    total_moves=total_moves,
                    remain_moves=remain_moves,
                ),
                callback_data="dice",
            )
    builder.adjust(1)
    return builder.as_markup()


async def ik_watch_results_game(link_on_message: str):
    builder = InlineKeyboardBuilder()
    builder.button(text=await get_text_button("watch_result"), url=link_on_message)
    builder.adjust(1)
    return builder.as_markup()
