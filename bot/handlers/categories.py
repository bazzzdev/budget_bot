from aiogram import Router, types
from aiogram.enums import ChatType
from aiogram.filters import Command
from sqlalchemy import text
from sqlalchemy.future import select

from bot.keyboards.menu import menu_inline_keyboard
from bot.models.models import Context, Category
from bot.services.db import get_async_session
from bot.services.utils import get_context, is_admin
from bot.utils.logger import logger

router = Router()

@router.message(Command("add"))
async def add_category_handler(message: types.Message):
    """
    Добавляет новую категорию в текущий групповой чат.
    Доступно только администраторам групп.
    """
    # Проверка типа чата
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("Добавлять категории можно только в группах.", reply_markup=menu_inline_keyboard())
        return

    # Проверка прав администратора
    if not await is_admin(message):
        await message.reply("Добавлять категории могут только администраторы.", reply_markup=menu_inline_keyboard())
        return

    # Получение названия категории из аргументов команды
    args = (
        message.text.removeprefix("/add@smartspendsbot")
        .removeprefix("/add")
        .strip()
    )
    if not args:
        await message.reply("Укажите название категории, например:\n/add кафе", reply_markup=menu_inline_keyboard())
        return

    async with get_async_session() as session:
        context = await get_context(session, message.chat)
        # Проверка на существование категории
        result = await session.execute(
            select(Category).where(
                Category.context_id == context.id,
                Category.title.ilike(args),
            )
        )
        existing = result.scalars().first()
        if existing:
            if existing.is_deleted:
                existing.is_deleted = False
                await session.commit()
                await message.reply(f"Категория '{args}' восстановлена!", reply_markup=menu_inline_keyboard())
            else:
                await message.reply(f"Категория '{args}' уже существует.", reply_markup=menu_inline_keyboard())
            return

        # Создание новой категории
        category = Category(title=args, context_id=context.id, is_default=False, is_deleted=False)
        session.add(category)
        await session.commit()
        await message.reply(f"Категория '{args}' успешно добавлена!", reply_markup=menu_inline_keyboard())

@router.message(Command("del"))
async def delete_category_handler(message: types.Message):
    """
    Логически удаляет категорию в текущем групповом чате.
    Доступно только администраторам групп.
    """
    # Проверка типа чата
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("Удалять категории можно только в группах.", reply_markup=menu_inline_keyboard())
        return

    # Проверка прав администратора
    if not await is_admin(message):
        await message.reply("Удалять категории могут только администраторы.", reply_markup=menu_inline_keyboard())
        return

    # Получение названия категории из аргументов команды
    args = (
        message.text.removeprefix("/del@smartspendsbot")
        .removeprefix("/del")
        .strip()
    )
    if not args:
        await message.reply("Укажите название категории, например:\n/del кафе", reply_markup=menu_inline_keyboard())
        return

    async with get_async_session() as session:
        context = await get_context(session, message.chat)
        # Поиск категории
        result = await session.execute(
            select(Category).where(
                Category.context_id == context.id,
                Category.title.ilike(args),
                Category.is_deleted == False,
            )
        )
        category = result.scalars().first()
        if not category:
            await message.reply(f"Категория '{args}' не найдена.", reply_markup=menu_inline_keyboard())
            return

        # Логическое удаление категории
        category.is_deleted = True
        await session.commit()
        await message.reply(f"Категория '{args}' успешно удалена.", reply_markup=menu_inline_keyboard())

@router.message(Command("categories"))
async def list_categories_handler(message: types.Message):
    """
    Показывает список всех доступных категорий для текущего чата.
    """
    async with get_async_session() as session:
        context = await get_context(session, message.chat)
        # Получение списка категорий
        result = await session.execute(
            select(Category.title)
            .where(
                Category.context_id == context.id,
                Category.is_deleted == False
            )
            .order_by(Category.title)
        )
        categories = result.scalars().all()

        if not categories:
            await message.reply("В этом чате нет доступных категорий.", reply_markup=menu_inline_keyboard())
            return

        text = (
            "Доступные категории:\n"
            "- - - - - - - - - -\n"
            + "\n".join(f"• {cat}" for cat in categories)
            + "\n- - - - - - - - - -\n"
        )
        await message.reply(text, reply_markup=menu_inline_keyboard())

@router.message(Command("clearcontext"))
async def clear_context_handler(message: types.Message):
    """
    Полностью очищает контекст чата: удаляет все категории, расходы, доходы и сам контекст.
    Доступно только администраторам групп.
    """
    # Проверка типа чата
    logger.info(f"/clearcontext от пользователя {message.from_user.id} в чате {message.chat.id}")
    if message.chat.type not in [ChatType.GROUP, ChatType.SUPERGROUP]:
        await message.reply("Очищать контекст можно только в группах.", reply_markup=menu_inline_keyboard())
        return

    # Проверка прав администратора
    if not await is_admin(message):
        await message.reply("Очищать контекст могут только администраторы.", reply_markup=menu_inline_keyboard())
        return

    async with get_async_session() as session:
        # Поиск контекста чата
        result = await session.execute(
            select(Context).where(
                Context.context_id == message.chat.id,
                Context.context_type == message.chat.type
            )
        )
        context = result.scalars().first()
        if not context:
            await message.reply("Контекст для этого чата не найден.", reply_markup=menu_inline_keyboard())
            return

        # Удаление расходов, доходов, категорий и самого контекста
        await session.execute(
            text(
                "DELETE FROM expenses WHERE category_id IN (SELECT id FROM categories WHERE context_id = :context_id)"
            ),
            {"context_id": context.id}
        )
        await session.execute(
            text(
                "DELETE FROM incomes WHERE category_id IN (SELECT id FROM categories WHERE context_id = :context_id)"
            ),
            {"context_id": context.id}
        )
        await session.execute(
            Category.__table__.delete().where(Category.context_id == context.id)
        )
        await session.delete(context)
        await session.commit()
        await message.reply("Контекст, категории, расходы и доходы успешно удалены.", reply_markup=menu_inline_keyboard())