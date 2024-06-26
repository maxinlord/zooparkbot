import config
import asyncio
import aioschedule
from db import Base
from init_db_redis import redis
from aiogram import Bot, Dispatcher
from aiogram.enums import ParseMode
from aiogram.types import BotCommand
from init_db import _sessionmaker, _engine
from bot.handlers import setup_message_routers
from aiogram.fsm.storage.redis import RedisStorage
from bot.middlewares import (
    DBSessionMiddleware,
    CheckUser,
    CheckUnity,
    RegMove,
    ThrottlingMiddleware,
    CheckGame,
)
from aiogram.client.default import DefaultBotProperties
from sqlalchemy.ext.asyncio import AsyncSession, AsyncEngine
from jobs import (
    verification_referrals,
    reset_first_offer_bought,
    job_minute,
    job_sec,
    add_bonus_to_users,
    create_game_for_chat,
    reset_items_effect
)

bot: Bot = Bot(
    config.BOT_TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.HTML)
)


async def on_startup(_engine: AsyncEngine) -> None:
    async with _engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)


async def on_shutdown(session: AsyncSession) -> None:
    await session.close_all()


async def scheduler() -> None:
    # aioschedule.every(1).seconds.do(job_sec, bot=bot)
    aioschedule.every(1).seconds.do(job_minute, bot=bot)
    aioschedule.every().day.at("10:00").do(reset_items_effect)
    aioschedule.every().day.at("10:30").do(reset_first_offer_bought)
    aioschedule.every().day.at("11:00").do(add_bonus_to_users)
    aioschedule.every().day.at("13:00").do(create_game_for_chat, bot=bot)
    aioschedule.every().day.at("16:30").do(create_game_for_chat, bot=bot)
    aioschedule.every().day.at("20:00").do(create_game_for_chat, bot=bot)   
    aioschedule.every().day.at("21:00").do(verification_referrals, bot=bot)
    while True:
        await aioschedule.run_pending()
        await asyncio.sleep(1)


async def set_default_commands(bot: Bot):
    await bot.set_my_commands(
        [
            BotCommand(command="start", description="-"),
            BotCommand(command="calculator", description="-"),
            BotCommand(command="support", description="-"),
            BotCommand(command="donate", description="-"),
        ]
    )


async def main() -> None:

    dp = Dispatcher(_engine=_engine, storage=RedisStorage(redis=redis))

    dp.startup.register(on_startup)
    dp.shutdown.register(on_shutdown)

    dp.message.middleware(ThrottlingMiddleware())

    dp.message.middleware(DBSessionMiddleware(session_pool=_sessionmaker))
    dp.callback_query.middleware(DBSessionMiddleware(session_pool=_sessionmaker))
    dp.inline_query.middleware(DBSessionMiddleware(session_pool=_sessionmaker))
    dp.update.middleware(DBSessionMiddleware(session_pool=_sessionmaker))

    dp.message.middleware(CheckUser())
    dp.callback_query.middleware(CheckUser())
    dp.inline_query.middleware(CheckUser())

    dp.message.middleware(CheckUnity())
    dp.callback_query.middleware(CheckUnity())

    dp.message.middleware(CheckGame())
    dp.callback_query.middleware(CheckGame())

    dp.message.middleware(RegMove())

    message_routers = setup_message_routers()
    asyncio.create_task(scheduler())
    dp.include_router(message_routers)
    await set_default_commands(bot)
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
