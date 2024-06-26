from aiogram.filters import CommandObject, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User, MessageToSupport
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import (
    mention_html,
    income_,
    get_text_message,
    get_photo,
    get_photo_from_message,
    find_integers
)
from bot.keyboards import ik_choice_rate_calculator, rk_cancel, rk_main_menu, ik_im_take
from bot.filters import CompareDataByIndex, GetTextButton
from bot.states import UserState
from datetime import datetime
from config import CHAT_SUPPORT_ID

router = Router()
flags = {"throttling_key": "default"}


@router.message(Command(commands="usd"), StateFilter(any_state))
async def command_reset(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if not command.args:
        await message.answer("Не указана сумма и username")
        return
    args = command.args.split(" ")
    if len(args) < 2:
        await message.answer("Не указана сумма или username")
        return
    user_to_add = await session.scalar(select(User).where(User.username == args[1]))
    if not user_to_add:
        await message.answer("Пользователь не найден")
        return
    amount = int(args[0])
    mention = mention_html(id_user=user_to_add.id_user, name=user_to_add.nickname)
    text = f"Добавлено {amount} USD игроку {user_to_add.nickname}"
    if amount < 0:
        text = f"Убавлено {amount} USD у игрока {mention}"
    user_to_add.usd += amount
    await session.commit()
    await message.answer(text)
    mention = mention_html(id_user=user.id_user, name=f"{amount} USD")
    await message.bot.send_message(chat_id=user_to_add.id_user, text=mention)


@router.message(Command(commands="calculator"), StateFilter(any_state))
async def calculator(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
    edit: bool = False,
) -> None:
    await state.update_data(calculator_rate=None)
    income_1_min = await income_(session=session, user=user)
    income_multipliers = [5, 30, 60, 60 * 12]
    incomes = [income_1_min * multiplier for multiplier in income_multipliers]
    func = {True: message.edit_text, False: message.answer}
    await func[edit](
        text=await get_text_message(
            "info_calculator",
            i1m=income_1_min,
            i5m=incomes[0],
            i30m=incomes[1],
            i60m=incomes[2],
            i12h=incomes[3],
        ),
        reply_markup=await ik_choice_rate_calculator(session=session),
    )


@router.callback_query(StateFilter(any_state), CompareDataByIndex("calculator"))
async def calculator_rate(
    query: CallbackQuery,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    rate = int(query.data.split(":")[0])
    data = await state.get_data()
    if data.get("calculator_rate") == rate:
        await calculator(
            message=query.message,
            state=state,
            command=query,
            session=session,
            user=user,
            edit=True,
        )
        return
    await state.update_data(calculator_rate=rate)
    income_1_min = await income_(session=session, user=user)

    # Store multiplication results
    income_multipliers = [5, 30, 60, 60 * 12]
    incomes = [income_1_min * multiplier for multiplier in income_multipliers]

    # Calculate USD values
    usd_values = [income // rate for income in [income_1_min] + incomes]

    await query.message.edit_text(
        text=await get_text_message(
            "info_calculator_by_rate",
            i1m=income_1_min,
            i5m=incomes[0],
            i30m=incomes[1],
            i60m=incomes[2],
            i12h=incomes[3],
            u1m=usd_values[0],
            u5m=usd_values[1],
            u30m=usd_values[2],
            u60m=usd_values[3],
            u12h=usd_values[4],
        ),
        reply_markup=await ik_choice_rate_calculator(
            session=session, current_rate=rate
        ),
    )


@router.message(Command(commands="c"), StateFilter(any_state))
async def small_calculator(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
    edit: bool = False,
) -> None:
    if not command.args:
        await calculator(
            message=message,
            state=state,
            command=command,
            session=session,
            user=user,
        )
        return
    args = command.args.split(" ")
    if not await find_integers(args[0]):
        return await message.answer(text=await get_text_message("error_min"))
    if len(args) == 2 and not await find_integers(args[1]):
        return await message.answer(text=await get_text_message("error_rate"))
    if len(args) > 2:
        return await message.answer(text=await get_text_message("error_args"))
    min = await find_integers(args[0])
    rate = await find_integers(args[1]) if len(args) == 2 else None
    income_1_min = await income_(session=session, user=user)
    income_custom_min = income_1_min * min
    if rate:
        usd_values = income_custom_min // rate
        await message.answer(
            text=await get_text_message(
                "info_calculator_by_min_and_rate",
                m=min,
                i=income_custom_min,
                u=usd_values,
                r=rate,
            )
        )
        return
    await message.answer(
        text=await get_text_message(
            "info_calculator_by_custom_min",
            m=min,
            i=income_custom_min,
        )
    )


@router.message(Command(commands="p"), StateFilter(any_state))
async def photo_view(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    if not command.args:
        await message.answer(text=await get_text_message("error_args"))
        return
    try:
        photo = await get_photo(session=session, photo_name=command.args.strip())
    except Exception:
        await message.answer(text=await get_text_message("error_photo"))
        return
    await message.answer_photo(photo=photo)


@router.message(UserState.main_menu, Command(commands="support"))
async def support(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    await message.answer(
        text=await get_text_message("send_mess_to_support"),
        reply_markup=await rk_cancel(),
    )
    await state.set_state(UserState.send_mess_to_support)


@router.message(Command(commands="support"))
async def support_error(
    message: Message,
    state: FSMContext,
    command: CommandObject,
    session: AsyncSession,
    user: User | None,
) -> None:
    await message.answer(text=await get_text_message("support_call_from_main_menu"))


@router.message(UserState.send_mess_to_support, GetTextButton("cancel"), flags=flags)
async def cancel_send_mess_to_supp(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("canceled"), reply_markup=await rk_main_menu()
    )


@router.message(UserState.send_mess_to_support)
async def get_sended_message(
    message: Message,
    session: AsyncSession,
    state: FSMContext,
    user: User,
):
    photo_id = await get_photo_from_message(message)
    if photo_id and not message.caption:
        await message.answer(
            text=await get_text_message("error_message_without_caption"),
        )
        return
    message_to_support = MessageToSupport(
        idpk_user=user.idpk,
        question=message.caption if photo_id else message.text,
        id_message_question=message.message_id,
        photo_id=photo_id,
    )
    session.add(message_to_support)
    await session.flush()
    await state.set_state(UserState.main_menu)
    await message.answer(
        text=await get_text_message("wait_answer"), reply_markup=await rk_main_menu()
    )
    func = {
        False: message.bot.send_message,
        True: message.bot.send_photo,
    }
    text = await get_text_message(
        "new_mess_to_support",
        user=mention_html(id_user=user.id_user, name=user.nickname),
        text=message_to_support.question,
        idpk_user=user.idpk,
    )
    mess_data = {"photo": photo_id, "caption": text} if photo_id else {"text": text}
    msg: Message = await func[bool(photo_id)](
        chat_id=CHAT_SUPPORT_ID,
        **mess_data,
        reply_markup=await ik_im_take(idpk_message_to_support=message_to_support.idpk),
    )
    message_to_support.id_message = msg.message_id
    await session.commit()
