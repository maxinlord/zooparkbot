from aiogram import Router


def setup_message_routers() -> Router:
    from . import (
        start,
        referrals,
        commands,
        zoomarket,
        unity,
        unity_level,
        unity_members,
        unity_top,
        bank,
        top,
        bonus,
        inline_send_ref_link,
        random_merchant,
        rarity_shop,
        workshop_items,
        aviaries,
        account,
        any_unknown_message,
        errors,
    )

    router = Router()
    router.include_router(start.router)
    router.include_router(commands.router)
    router.include_router(referrals.router)
    router.include_router(zoomarket.router)
    router.include_router(unity.router)
    router.include_router(unity_level.router)
    router.include_router(unity_members.router)
    router.include_router(unity_top.router)
    router.include_router(bank.router)
    router.include_router(top.router)
    router.include_router(bonus.router)
    router.include_router(inline_send_ref_link.router)
    router.include_router(account.router)
    router.include_router(random_merchant.router)
    router.include_router(rarity_shop.router)
    router.include_router(workshop_items.router)
    router.include_router(aviaries.router)

    router.include_router(any_unknown_message.router)

    # router.include_router(errors.router)

    # router.include_router(bot_messages.router)
    return router
