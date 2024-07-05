from aiogram.filters import CommandObject, Command
from aiogram.types import Message, LabeledPrice, PreCheckoutQuery
from aiogram.exceptions import TelegramBadRequest
from aiogram import F, Bot, Router
from aiogram.fsm.context import FSMContext
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, Donate
from tools import (
    get_text_message,
    find_integers,
    get_value,
    add_to_currency,
    find_integers,
)

router = Router()
flags = {"throttling_key": "default"}
message_effect_id_heart = "5159385139981059251"


@router.message(Command(commands="donate"))
async def donate(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if not command.args:
        ONE_STAR_IS = await get_value(session=session, value_name="ONE_STAR_IS")
        return await message.answer(
            text=await get_text_message("donate_info", one_star_is=ONE_STAR_IS)
        )
    args = command.args
    if not await find_integers(args) or await find_integers(args) > 2500:
        return await message.answer(text=await get_text_message("donate_info"))
    amount = await find_integers(args)
    prices = [
        LabeledPrice(label="XTR", amount=amount),
    ]
    await message.answer_invoice(
        title=await get_text_message("title_base_donate"),
        description=await get_text_message("description_base_donate", amount=amount),
        prices=prices,
        provider_token="",
        payload="_",
        currency="XTR",
    )


@router.pre_checkout_query()
async def on_pre_checkout_query(
    pre_checkout_query: PreCheckoutQuery,
):
    await pre_checkout_query.answer(ok=True)


@router.message(F.successful_payment)
async def on_successful_payment(
    message: Message,
    state: FSMContext,
    session: AsyncSession,
    user: User | None,
):
    ONE_STAR_IS = await get_value(session=session, value_name="ONE_STAR_IS")
    paw_coins_to_add = message.successful_payment.total_amount * ONE_STAR_IS
    await add_to_currency(self=user, currency="paw_coins", amount=paw_coins_to_add)
    session.add(
        Donate(
            idpk_user=user.id,
            amount=message.successful_payment.total_amount,
            refund_id=message.successful_payment.telegram_payment_charge_id,
        )
    )
    await session.commit()
    await message.answer(
        text=await get_text_message(
            "thanks_for_donate", paw_coins_to_add=paw_coins_to_add
        ),
        message_effect_id=message_effect_id_heart,
    )


@router.message(Command("refund"))
async def cmd_refund(
    message: Message,
    bot: Bot,
    command: CommandObject,
):
    if message.from_user.id != 474701274:
        return await get_text_message("command_not_available")
    transaction_id = command.args
    if transaction_id is None:
        await message.answer(text=await get_text_message("refund_bad"))
        return
    try:
        await bot.refund_star_payment(
            user_id=message.from_user.id, telegram_payment_charge_id=transaction_id
        )
        await message.answer(text=await get_text_message("refund_good"))
    except TelegramBadRequest as error:
        if (
            "CHARGE_NOT_FOUND" in error.message
            or "CHARGE_ALREADY_REFUNDED" not in error.message
        ):
            text = await get_text_message("refund_code_not_found")
        else:
            text = await get_text_message("refund_already_refunded")
        await message.answer(text)
        return
