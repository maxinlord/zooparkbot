from aiogram import Bot
from sqlalchemy import select, update, and_
from db import User
from init_db import _sessionmaker_for_func
from tools import referrer_bonus, referral_bonus, get_text_message


async def job_sec(bot: Bot) -> None:
    pass


async def job_minute() -> None:
    pass

async def verification_referrals(bot: Bot):
    async with _sessionmaker_for_func() as session:
        users = await session.scalars(select(User).where(and_(User.id_referrer != None,
                                                              User.referral_verification == False)))
        users = users.all()
        QUANTITY_MOVES_TO_PASS = 100
        QUANTITY_RUB_TO_PASS = 1000
        QUANTITY_USD_TO_PASS = 1000
        for user in users:
            
            if user.moves < QUANTITY_MOVES_TO_PASS:
                continue
            if user.amount_expenses_rub < QUANTITY_RUB_TO_PASS:
                continue
            if user.amount_expenses_usd < QUANTITY_USD_TO_PASS:
                continue
            await referrer_bonus()
            referrer: User = await session.get(User, user.id_referrer)
            await bot.send_message(chat_id=referrer.id_user, text=await get_text_message('you_got_bonus_referrer'))
            await referral_bonus()
            await bot.send_message(chat_id=user.id_user, text=await get_text_message('you_got_bonus_referral'))
            user.referral_verification = True
            await session.commit()


async def test_job() -> None:
    from db import Animal 
    async with _sessionmaker_for_func() as session:
        r = await session.scalars(select(Animal.code_name))
        print(r.all())
            

