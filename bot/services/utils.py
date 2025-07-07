import re
from datetime import datetime, timedelta

from aiogram import types
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select

from bot.models.models import Category, Context, User

def parse_date_arg(arg: str) -> tuple[datetime, datetime, str] | None:
    """
    Парсит строку с датой или диапазоном дат, возвращает кортеж (date_from, date_to, описание).
    Поддерживаемые форматы:
      - "day" — сегодня
      - "week" — текущая неделя
      - "month" — текущий месяц
      - "ДД.ММ.ГГГГ" — конкретная дата
      - "ДД.ММ.ГГГГ - ДД.ММ.ГГГГ" — диапазон дат
    Возвращает None, если формат не распознан.
    """
    now = datetime.utcnow()
    arg = arg.strip().lower()
    try:
        if arg == "day":
            # Сегодняшний день с полуночи до текущего времени
            date_from = now.replace(hour=0, minute=0, second=0, microsecond=0)
            return date_from, now, "за сегодня"
        elif arg == "week":
            # С начала текущей недели (понедельник) до текущего времени
            date_from = (now - timedelta(days=now.weekday())).replace(hour=0, minute=0, second=0, microsecond=0)
            return date_from, now, "за неделю"
        elif arg == "month":
            # С первого числа текущего месяца до текущего времени
            date_from = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
            return date_from, now, "за месяц"
        elif re.match(r"^\d{2}\.\d{2}\.\d{4}$", arg):
            # Конкретная дата в формате ДД.ММ.ГГГГ
            date_from = datetime.strptime(arg, "%d.%m.%Y")
            date_to = date_from + timedelta(days=1)
            return date_from, date_to, f"за {arg}"
        elif re.match(r"^\d{2}\.\d{2}\.\d{4}\s*-\s*\d{2}\.\d{2}\.\d{4}$", arg):
            # Диапазон дат в формате ДД.ММ.ГГГГ - ДД.ММ.ГГГГ
            start_str, end_str = [p.strip() for p in arg.split("-")]
            date_from = datetime.strptime(start_str, "%d.%m.%Y")
            date_to = datetime.strptime(end_str, "%d.%m.%Y") + timedelta(days=1)
            return date_from, date_to, f"c {start_str} по {end_str}"
    except Exception:
        # В случае ошибки парсинга возвращаем None
        pass
    return None

async def get_or_create_context(session, chat):
    """
    Получает контекст чата (Context) по id и типу.
    Если не найден — создает новый контекст.
    """
    result = await session.execute(
        select(Context).where(Context.context_id == chat.id, Context.context_type == chat.type)
    )
    context = result.scalars().first()
    if not context:
        context = Context(context_id=chat.id, context_type=chat.type)
        session.add(context)
        await session.commit()
    return context

async def get_user(session, tg_id: int):
    """
    Получает пользователя (User) по Telegram ID.
    Возвращает None, если пользователь не найден.
    """
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    return result.scalars().first()

async def get_or_create_user(session, tg_user):
    """
    Получает пользователя (User) по Telegram ID.
    Если не найден — создает нового пользователя.
    """
    result = await session.execute(select(User).where(User.tg_id == tg_user.id))
    user = result.scalar_one_or_none()
    if not user:
        user = User(
            tg_id=tg_user.id,
            username=tg_user.username,
            first_name=tg_user.first_name
        )
        session.add(user)
        await session.commit()
    return user

async def get_context(session, chat: types.Chat):
    """
    Получает контекст чата (Context) по id и типу.
    Если не найден — создает новый контекст и добавляет стандартные категории.
    """
    result = await session.execute(
        select(Context).where(Context.context_id == chat.id, Context.context_type == chat.type)
    )
    context = result.scalars().first()
    if not context:
        context = Context(context_id=chat.id, context_type=chat.type)
        session.add(context)
        await session.commit()
        await session.refresh(context)
        # Добавление стандартных категорий для нового чата
        default_categories = [
            "аванс", "авто", "алкоголь", "аптека", "бензин", "больницы", "дом", "зарплата", "ипотека", "кафе",
            "коммунальные", "красота", "кредит", "образование", "одежда", "питомцы", "подарки",
            "продукты", "прочее", "путешествия", "развлечения", "сигареты", "спорт", "транспорт",
            "участок", "хобби", "хозтовары", "электроника"
        ]
        for cat in default_categories:
            session.add(Category(title=cat, context_id=context.id, is_default=True, is_deleted=False))
        await session.commit()
    return context

async def is_admin(message: types.Message) -> bool:
    """
    Проверяет, является ли пользователь администратором или создателем чата.
    Возвращает True, если да, иначе False.
    """
    try:
        member = await message.chat.get_member(message.from_user.id)
        return member.status in ["administrator", "creator"]
    except Exception:
        # В случае ошибки (например, бот не может получить статус) возвращаем False
        return False

async def get_category(session: AsyncSession, title: str, context: Context) -> Category | None:
    """
    Получает категорию (Category) по названию (title) и контексту (context).
    Категория должна быть не удалена.
    Возвращает None, если категория не найдена.
    """
    result = await session.execute(
        select(Category)
        .where(Category.title.ilike(title))
        .where(Category.context_id == context.id)
        .where(Category.is_deleted == False)
    )
    return result.scalars().first()