import asyncio
import logging

import httpx
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.redis import RedisStorage
from aiogram.utils.i18n import I18n, I18nMiddleware, SimpleI18nMiddleware

import settings
from handlers import authorization, common, all_announcements, main_menu, create_announcement
from middlewares.auth import AuthMiddleware
from middlewares.locale import LocaleMiddleware

i18n = I18n(path="locales", default_locale="ru", domain="messages")
bot = Bot(token=settings.BOT_TOKEN)
httpx_client = httpx.AsyncClient(http2=True)
redis_storage = RedisStorage(settings.REDIS_STORAGE)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher(storage=redis_storage)
    dp.message.outer_middleware(LocaleMiddleware(i18n))
    dp.callback_query.outer_middleware(LocaleMiddleware(i18n))

    dp.callback_query.outer_middleware(AuthMiddleware())

    # Альтернативный вариант регистрации роутеров по одному на строку
    dp.include_router(authorization.router)
    dp.include_router(common.router)
    dp.include_router(all_announcements.router)
    dp.include_router(main_menu.router)
    dp.include_router(create_announcement.router)
    # # Запускаем бота и пропускаем все накопленные входящие
    # # Да, этот метод можно вызвать даже если у вас поллинг

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
