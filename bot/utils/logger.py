from loguru import logger

logger.add("bot.log", rotation="1 week", level="INFO", encoding="utf-8")