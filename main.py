import asyncio

from bot.handlers import all_handlers
from bot.settings import bot, dp
from bot.utils.logger import logger

for router in all_handlers:
    dp.include_router(router)

async def main():
    logger.info("Бот запущен")
    await dp.start_polling(bot)

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        logger.info("Бот остановлен вручную")
