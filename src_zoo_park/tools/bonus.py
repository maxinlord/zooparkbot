from sqlalchemy import select
from db import User, Value
from init_db import _sessionmaker_for_func


async def referral_bonus():
    print("referral_get_bonus")


async def referrer_bonus():
    print("referrer_get_bonus")


async def bonus_for_sub_on_chat():
    print("bonus_for_sub_on_chat")


async def bonus_for_sub_on_channel():
    print("bonus_for_sub_on_channel")


async def bonus():
    print("bonus")