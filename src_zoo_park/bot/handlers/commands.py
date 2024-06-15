from aiogram.filters import CommandObject, Command
from aiogram.types import Message, CallbackQuery
from aiogram import Router
from aiogram.fsm.context import FSMContext
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from db import User
from aiogram.filters import StateFilter
from aiogram.fsm.state import any_state
from tools import mention_html, income_, get_text_message
from bot.keyboards import ik_choice_rate_calculator
from bot.filters import CompareDataByIndex

router = Router()


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
    if not args[0].isdigit():
        return await message.answer(text=await get_text_message("error_min"))
    if len(args) == 2 and not args[1].isdigit():
        return await message.answer(text=await get_text_message("error_rate"))
    if len(args) > 2:
        return await message.answer(text=await get_text_message("error_args"))
    min = int(args[0])
    rate = int(args[1]) if len(args) == 2 else None
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
