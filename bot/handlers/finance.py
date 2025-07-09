import re
from datetime import datetime, UTC
from decimal import Decimal, InvalidOperation

from aiogram import Router, types, F
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from sqlalchemy.future import select

from bot.models.models import User, Expense, Income
from bot.services.db import get_async_session
from bot.services.utils import get_or_create_user, get_or_create_context, get_category

router = Router()

@router.message(F.text)
async def handle_expense_income(message: types.Message):
    """
    Обрабатывает сообщения с расходами и доходами.
    Формат: `1000 категория` (расход) или `+5000 категория` (доход).
    """
    text = message.text.strip()

    if text.startswith("/"):
        # Игнорируем команды
        return

    # Проверяем формат сообщения: сумма категория или +сумма категория
    if not re.match(r"^\+?\d+([.,]\d+)?\s+\S+", text):
        return  # Не обрабатываем неподходящие сообщения

    async with get_async_session() as session:
        user_tg = message.from_user
        chat = message.chat

        # Определяем тип операции (доход или расход)
        if text.startswith("+"):
            operation_type = "income"
            text = text[1:].strip()
        else:
            operation_type = "expense"

        try:
            parts = text.split(maxsplit=1)
            if len(parts) != 2:
                await message.reply(
                    "Неверный формат сообщения. Используйте:\n\n"
                    "Для расхода: `1000 категория`\n"
                    "Для дохода: `+5000 категория`",
                    parse_mode="Markdown"
                )
                return

            amount_str, category_title = parts
            amount = Decimal(amount_str.replace(",", "."))
            if amount <= 0:
                await message.reply("Сумма должна быть положительным числом.")
                return
        except (InvalidOperation, ValueError):
            await message.reply(
                "Неверная сумма. Введите число, например: `1000 бензин` или `+50000 зарплата`.\n\n"
                "Список доступных категорий: `/categories`",
                parse_mode="Markdown"
            )
            return

        # Получаем пользователя, контекст и категорию
        user = await get_or_create_user(session, user_tg)
        context = await get_or_create_context(session, chat)
        category = await get_category(session, category_title, context)
        if not category:
            await message.reply(
                f"Категория '{category_title}' не найдена в этом чате. "
                "Используйте /categories чтобы посмотреть доступные категории."
            )
            return

        now = datetime.now(UTC).replace(tzinfo=None)
        # Создаем запись о расходе или доходе
        if operation_type == "expense":
            record = Expense(
                user_id=user.id, context_id=context.id, category_id=category.id,
                amount=amount, created_at=now
            )
        else:
            record = Income(
                user_id=user.id, context_id=context.id, category_id=category.id,
                amount=amount, created_at=now
            )

        session.add(record)
        await session.commit()

        # Кнопка для удаления записи
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [
                InlineKeyboardButton(
                    text=f"Удалить {'расход' if operation_type == 'expense' else 'доход'}",
                    callback_data=f"delete_{operation_type}:{record.id}"
                )
            ]
        ])

        await message.answer(
            f"{'Расход' if operation_type == 'expense' else 'Доход'} добавлен!\n"
            f"Сумма: {amount}\n"
            f"Категория: {category.title}\n"
            f"Дата: {now.strftime('%d.%m.%Y %H:%M')}\n"
            f"Пользователь: @{user_tg.username or user_tg.first_name}",
            reply_markup=keyboard
        )

@router.callback_query(lambda c: c.data and c.data.startswith(("delete_expense:", "delete_income:")))
async def delete_record_callback(callback: CallbackQuery):
    """
    Обрабатывает нажатие на кнопку удаления расхода или дохода.
    Удалить запись может только ее автор.
    """
    data = callback.data
    user_tg = callback.from_user

    op_type, record_id_str = data.split(":")
    record_id = int(record_id_str)

    async with get_async_session() as session:
        # Получаем запись по типу (расход или доход)
        if op_type == "delete_expense":
            record = await session.get(Expense, record_id)
        else:
            record = await session.get(Income, record_id)

        if not record:
            await callback.answer("Запись уже удалена или не найдена.", show_alert=True)
            return

        # Проверяем, что удаляет автор записи
        user_result = await session.execute(select(User).where(User.tg_id == user_tg.id))
        user = user_result.scalars().first()
        if not user or user.id != record.user_id:
            await callback.answer("Вы не можете удалить эту запись.", show_alert=True)
            return

        await session.delete(record)
        await session.commit()

        await callback.message.edit_text("Запись удалена.")
        await callback.answer()
