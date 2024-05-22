from aiogram import Router


def setup_message_routers() -> Router:
    from . import (
        start,
        referrals,
        commands,
        zoomarket,
        random_merchant,
        any_unknown_message,
        errors,
    )

    router = Router()
    router.include_router(start.router)
    router.include_router(commands.router)
    router.include_router(referrals.router)
    router.include_router(zoomarket.router)
    router.include_router(random_merchant.router)

    router.include_router(any_unknown_message.router)

    # router.include_router(errors.router)

    # router.include_router(bot_messages.router)
    return router
