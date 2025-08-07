from datetime import UTC, datetime, timedelta

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from sqlalchemy import func
from sqlalchemy.future import select

from bot.keyboards.menu import menu_inline_keyboard
from bot.models.models import Category, Expense, Income
from bot.services.db import get_async_session
from bot.services.utils import (
    get_or_create_context,
    get_user,
    get_user_display,
    parse_date_arg,
)

router = Router()


@router.message(Command("statcat"))
async def statcat_handler(callback: CallbackQuery, period):
    """
    Обрабатывает команду /statcat и возвращает статистику по категориям за выбранный период.
    Показывает суммы доходов и расходов по каждой категории.
    """
    parsed = parse_date_arg(period or "")
    if not parsed:
        await callback.message.reply(
            "Используйте: /statcat day, /statcat week, /statcat month, /statcat dd.mm.yyyy или /statcat dd.mm.yyyy - dd.mm.yyyy"
        )
        return

    date_from, date_to, period_text = parsed

    async with get_async_session() as session:
        # Получаем контекст чата и пользователя
        context = await get_or_create_context(session, callback.message.chat)
        user = await get_user(session, callback.from_user.id)

        if not user:
            await callback.message.reply("Пользователь не найден.")
            return

        # Доходы по категориям
        income_rows = (
            await session.execute(
                select(Category.title, func.sum(Income.amount))
                .join(Income, Income.category_id == Category.id)
                .where(
                    Income.context_id == context.id,
                    Income.user_id == user.id,
                    Income.created_at >= date_from,
                    Income.created_at < date_to,
                    Category.is_deleted == False,
                )
                .group_by(Category.title)
                .order_by(func.sum(Income.amount).desc())
            )
        ).all()

        # Расходы по категориям
        expense_rows = (
            await session.execute(
                select(Category.title, func.sum(Expense.amount))
                .join(Expense, Expense.category_id == Category.id)
                .where(
                    Expense.context_id == context.id,
                    Expense.user_id == user.id,
                    Expense.created_at >= date_from,
                    Expense.created_at < date_to,
                    Category.is_deleted == False,
                )
                .group_by(Category.title)
                .order_by(func.sum(Expense.amount).desc())
            )
        ).all()

    # Имя пользователя
    username = callback.from_user.username
    user_display = (
        f"@{username}" if username else (callback.from_user.full_name or "Аноним")
    )

    # Суммы
    total_income = sum(amount for _, amount in income_rows) if income_rows else 0
    total_expense = sum(amount for _, amount in expense_rows) if expense_rows else 0

    # Формируем текст
    text = f"Статистика для {user_display} по категориям {period_text}\n\n"

    text += "🟢 Доход:\n- - - - - - - - - -\n"
    if income_rows:
        text += "\n".join([f"{int(amount)} {title}" for title, amount in income_rows])
    else:
        text += "нет"
    text += f"\n- - - - - - - - - -\nИтого: {int(total_income)}\n"

    text += "\n🔴 Расход:\n- - - - - - - - - -\n"
    if expense_rows:
        text += "\n".join([f"{int(amount)} {title}" for title, amount in expense_rows])
    else:
        text += "нет"
    text += f"\n- - - - - - - - - -\nИтого: {int(total_expense)}"

    # Отправляем статистику
    await callback.message.answer(text, reply_markup=menu_inline_keyboard())


@router.message(Command("statdetail"))
async def statdetail_handler(callback: CallbackQuery, period):
    """
    Обрабатывает команду /statdetail и возвращает детальную статистику по всем операциям пользователя за текущий день.
    Показывает список всех доходов и расходов с датой, категорией и суммой.
    """
    now = datetime.now(UTC)
    date_from = now.replace(hour=0, minute=0, second=0, microsecond=0).replace(
        tzinfo=None
    )
    date_to = (date_from + timedelta(days=1)).replace(tzinfo=None)

    async with get_async_session() as session:
        # Получаем контекст чата и пользователя
        context = await get_or_create_context(session, callback.message.chat)
        user = await get_user(session, callback.from_user.id)

        if not user:
            await callback.message.reply("Пользователь не найден.")
            return

        # Доходы за день
        income_rows = (
            await session.execute(
                select(Income.created_at, Income.amount, Category.title)
                .join(Category, Income.category_id == Category.id)
                .where(
                    Income.context_id == context.id,
                    Income.user_id == user.id,
                    Income.created_at >= date_from,
                    Income.created_at < date_to,
                    Category.is_deleted == False,
                )
                .order_by(Income.created_at)
            )
        ).all()

        # Расходы за день
        expense_rows = (
            await session.execute(
                select(Expense.created_at, Expense.amount, Category.title)
                .join(Category, Expense.category_id == Category.id)
                .where(
                    Expense.context_id == context.id,
                    Expense.user_id == user.id,
                    Expense.created_at >= date_from,
                    Expense.created_at < date_to,
                    Category.is_deleted == False,
                )
                .order_by(Expense.created_at)
            )
        ).all()

    def fmt_rows(rows):
        """Форматирует строки для вывода операций."""
        return "\n".join(
            f"{dt.strftime('%d.%m.%Y - %H:%M')} | {int(amount)} • {cat}"
            for dt, amount, cat in rows
        )

    income_text = fmt_rows(income_rows)
    income_total = sum(int(amount) for _, amount, _ in income_rows)

    expense_text = fmt_rows(expense_rows)
    expense_total = sum(int(amount) for _, amount, _ in expense_rows)

    user_display = get_user_display(callback.from_user)

    text = f"Детальная статистика за {now.strftime('%d.%m.%Y')} для {user_display}\n\n"
    text += "🟢 Доход\n"
    text += "- - - - - - - - - -\n"
    text += income_text or "нет"
    text += "\n- - - - - - - - - -\n"
    text += f"Итого: {income_total}\n\n"
    text += "🔴 Расход\n"
    text += "- - - - - - - - - -\n"
    text += expense_text or "нет"
    text += "\n- - - - - - - - - -\n"
    text += f"Итого: {expense_total}"

    # Отправляем детальную статистику за день
    await callback.message.answer(text, reply_markup=menu_inline_keyboard())
