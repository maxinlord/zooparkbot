from aiogram import Router


def setup_message_routers() -> Router:
    from . import (
        start,
        errors,
        commands
    )

    router = Router()
    router.include_router(start.router)
    router.include_router(commands.router)
    # router.include_router(errors.router)

    # router.include_router(bot_messages.router)
    return router
