from sqlalchemy.ext.asyncio import create_async_engine, async_sessionmaker

from bot.config import settings

# Создание асинхронного движка базы данных с использованием URL из настроек
engine = create_async_engine(settings.database_url, echo=False)

# Создание фабрики асинхронных сессий
AsyncSessionLocal = async_sessionmaker(engine, expire_on_commit=False)

# Функция для получения новой асинхронной сессии
def get_async_session():
    return AsyncSessionLocal()
