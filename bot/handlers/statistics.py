from datetime import datetime, timedelta, UTC

from aiogram import Router
from aiogram.filters import Command
from aiogram.types import CallbackQuery
from sqlalchemy import func
from sqlalchemy.future import select

from bot.keyboards.menu import menu_inline_keyboard
from bot.models.models import Income, Expense, Category
from bot.services.db import get_async_session
from bot.services.utils import parse_date_arg, get_or_create_context, get_user

router = Router()

@router.message(Command("stat"))
async def stat_handler(callback: CallbackQuery, period):
    """
    Обрабатывает команду /stat и возвращает сумму доходов и расходов пользователя за выбранный период.
    Параметры периода: day, week, month, дата или диапазон дат.
    """
    parsed = parse_date_arg(period or "")
    if not parsed:
        await callback.message.reply(
            "Используйте: /stat day, /stat week, /stat month, /stat dd.mm.yyyy или /stat dd.mm.yyyy - dd.mm.yyyy"
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

        # Суммируем доходы за период
        income_sum = (await session.execute(
            select(func.sum(Income.amount)).where(
                Income.context_id == context.id,
                Income.user_id == user.id,
                Income.created_at >= date_from,
                Income.created_at < date_to
            )
        )).scalar() or 0

        # Суммируем расходы за период
        expense_sum = (await session.execute(
            select(func.sum(Expense.amount)).where(
                Expense.context_id == context.id,
                Expense.user_id == user.id,
                Expense.created_at >= date_from,
                Expense.created_at < date_to
            )
        )).scalar() or 0

    text = (
        f"Статистика {period_text}:\n"
        f"🟢 Доход: <b>{income_sum}</b>\n"
        f"🔴 Расход: <b>{expense_sum}</b>"
    )
    # Отправляем пользователю итоговую статистику
    await callback.message.answer(text, parse_mode="HTML", reply_markup=menu_inline_keyboard())

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
        income_rows = (await session.execute(
            select(Category.title, func.sum(Income.amount))
            .join(Income, Income.category_id == Category.id)
            .where(
                Income.context_id == context.id,
                Income.user_id == user.id,
                Income.created_at >= date_from,
                Income.created_at < date_to,
                Category.is_deleted == False
            )
            .group_by(Category.title)
            .order_by(func.sum(Income.amount).desc())
        )).all()

        # Расходы по категориям
        expense_rows = (await session.execute(
            select(Category.title, func.sum(Expense.amount))
            .join(Expense, Expense.category_id == Category.id)
            .where(
                Expense.context_id == context.id,
                Expense.user_id == user.id,
                Expense.created_at >= date_from,
                Expense.created_at < date_to,
                Category.is_deleted == False
            )
            .group_by(Category.title)
            .order_by(func.sum(Expense.amount).desc())
        )).all()

    text = f"Статистика по категориям {period_text}:\n\n"
    text += ("🟢 Доход:\n" + "- - - - - - - - - -\n" +
             ("\n".join([f"{int(amount)} {title}" for title, amount in income_rows]) or "нет"))
    text += "\n- - - - - - - - - -\n"
    text += ("\n🔴 Расход:\n" + "- - - - - - - - - -\n" +
             ("\n".join([f"{int(amount)} {title}" for title, amount in expense_rows]) or "нет"))
    text += "\n- - - - - - - - - -\n"

    # Отправляем статистику по категориям
    await callback.message.answer(text, reply_markup=menu_inline_keyboard())

@router.message(Command("statdetail"))
async def statdetail_handler(callback: CallbackQuery, period):
    """
    Обрабатывает команду /statdetail и возвращает детальную статистику по всем операциям пользователя за текущий день.
    Показывает список всех доходов и расходов с датой, категорией и суммой.
    """
    now = datetime.now(UTC)
    date_from = now.replace(hour=0, minute=0, second=0, microsecond=0).replace(tzinfo=None)
    date_to = (date_from + timedelta(days=1)).replace(tzinfo=None)

    async with get_async_session() as session:
        # Получаем контекст чата и пользователя
        context = await get_or_create_context(session, callback.message.chat)
        user = await get_user(session, callback.from_user.id)

        if not user:
            await callback.message.reply("Пользователь не найден.")
            return

        # Доходы за день
        income_rows = (await session.execute(
            select(Income.created_at, Income.amount, Category.title)
            .join(Category, Income.category_id == Category.id)
            .where(
                Income.context_id == context.id,
                Income.user_id == user.id,
                Income.created_at >= date_from,
                Income.created_at < date_to,
                Category.is_deleted == False
            )
            .order_by(Income.created_at)
        )).all()

        # Расходы за день
        expense_rows = (await session.execute(
            select(Expense.created_at, Expense.amount, Category.title)
            .join(Category, Expense.category_id == Category.id)
            .where(
                Expense.context_id == context.id,
                Expense.user_id == user.id,
                Expense.created_at >= date_from,
                Expense.created_at < date_to,
                Category.is_deleted == False
            )
            .order_by(Expense.created_at)
        )).all()

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

    text = f"Детальная статистика за {now.strftime('%d.%m.%Y')}\n\n"
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