import asyncio
import logging

from aiogram import Bot, Dispatcher
from handlers import *
import settings

bot = Bot(token=settings.BOT_TOKEN)


async def main():
    logging.basicConfig(level=logging.INFO)
    dp = Dispatcher()
    # Альтернативный вариант регистрации роутеров по одному на строку
    # dp.include_router(authorization.router)
    # dp.include_router(common.router)
    # dp.include_router(all_announcements.router)
    # dp.include_router(main_menu.router)
    # dp.include_router(create_announcement.router)
    # # Запускаем бота и пропускаем все накопленные входящие
    # # Да, этот метод можно вызвать даже если у вас поллинг

    await bot.delete_webhook(drop_pending_updates=True)
    await dp.start_polling(bot, skip_updates=True)


if __name__ == "__main__":
    asyncio.run(main())
