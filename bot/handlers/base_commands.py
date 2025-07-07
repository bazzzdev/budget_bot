from aiogram import Router
from aiogram.filters import Command
from aiogram.types import Message

from bot.handlers.categories import get_context
from bot.keyboards.menu import menu_inline_keyboard
from bot.services.db import AsyncSessionLocal
from bot.services.utils import get_or_create_user
from bot.utils.logger import logger

router = Router()

@router.message(Command("start"))
async def start_handler(message: Message):
    """
    Обрабатывает команду /start.
    Регистрирует пользователя в базе данных и отправляет приветственное сообщение.
    """
    logger.info(f"/start от пользователя {message.from_user.id} в чате {message.chat.id}")
    async with AsyncSessionLocal() as session:
        await get_or_create_user(session, message.from_user)
        await get_context(session, message.chat)

    await message.answer(
        f"Привет, <b>{message.from_user.first_name}</b>!\n"
        f"Вы начали работу с ботом в чате <code>{message.chat.id}</code>\n"
        f"Язык: Русский (по умолчанию)",
        reply_markup=menu_inline_keyboard()
    )

@router.message(Command("commands"))
async def commands_handler(message: Message):
    """
    Обрабатывает команду /commands.
    Показывает список доступных команд и краткое описание их назначения.
    """
    text = (
        "Доступные команды:\n"
        "\n"
        "<code>+сумма категория</code> — добавить доход, например: <b>+5000 зарплата</b>\n"
        "\n"
        "<code>сумма категория</code> — добавить расход, например: <b>1000 кафе</b>\n"
        "\n"
        "/stat day | week | month | ДД.ММ.ГГГГ | ДД.ММ.ГГГГ - ДД.ММ.ГГГГ — показать сумму доходов/расходов за день, неделю, месяц, дату, период\n"
        "\n"
        "/statcat day | week | month | ДД.ММ.ГГГГ | ДД.ММ.ГГГГ - ДД.ММ.ГГГГ — показать статистику доходов/расходов по категориям за день, неделю, месяц, дату, период\n"
        "\n"
        "/statdetail day — показать детализацию доходов/расходов с начала дня\n"
        "\n"
        "/categories — Показать список доступных категорий\n"
        "\n"
        "/add категория — добавить категорию <b>(только для админов в группе)</b>\n"
        "\n"
        "/del категория — удалить категорию <b>(только для админов в группе)</b>\n"
        "\n"
        "/clearcontext — удалить все категории и историю доходов/расходов <b>(только для админов в группе)</b>\n"
        "\n"
        "/commands — показать это сообщение\n"
        "\n"
        "/help — помощь\n"
    )
    await message.answer(text, reply_markup=menu_inline_keyboard())

@router.message(Command("help"))
async def help_handler(message: Message):
    """
    Обрабатывает команду /help.
    Показывает справочную информацию и контакты для связи.
    """
    text = (
        "По всем вопросам: @bazzzvl\n"
        "\n"
        "| <a href='https://github.com/bazzzdev/budget_bot'>GitHub</a> |"
    )
    await message.answer(text, reply_markup=menu_inline_keyboard())