from unittest.mock import AsyncMock, patch, MagicMock

import pytest

import bot.handlers.categories as handlers


@pytest.mark.asyncio
@patch("bot.handlers.categories.is_admin", new_callable=AsyncMock)
@patch("bot.handlers.categories.get_async_session")
@patch("bot.handlers.categories.get_context", new_callable=AsyncMock)
async def test_add_category_handler_success(get_context_mock, get_async_session_mock, is_admin_mock):
    is_admin_mock.return_value = True
    message = MagicMock()
    message.text = "/add Тест"
    message.reply = AsyncMock()
    message.chat.id = 123
    message.chat.type = "group"

    session = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=None)))))
    get_async_session_mock.return_value.__aenter__.return_value = session
    get_context_mock.return_value = MagicMock(id=1)
    session.commit = AsyncMock()

    await handlers.add_category_handler(message)
    print(message.reply.call_args_list)
    message.reply.assert_called_with("Категория 'Тест' успешно добавлена!", reply_markup=handlers.menu_inline_keyboard())

@pytest.mark.asyncio
@patch("bot.handlers.categories.is_admin", new_callable=AsyncMock)
async def test_add_category_handler_not_admin(is_admin_mock):
    is_admin_mock.return_value = False
    message = MagicMock()
    message.text = "/add Тест"
    message.reply = AsyncMock()
    message.chat.id = 123
    message.chat.type = "group"

    await handlers.add_category_handler(message)
    message.reply.assert_called_with("Добавлять категории могут только администраторы.", reply_markup=handlers.menu_inline_keyboard())

@pytest.mark.asyncio
@patch("bot.handlers.categories.is_admin", new_callable=AsyncMock)
async def test_delete_category_handler_no_args(is_admin_mock):
    is_admin_mock.return_value = True
    message = MagicMock()
    message.text = "/del"
    message.reply = AsyncMock()
    message.chat.id = 123
    message.chat.type = "group"

    await handlers.delete_category_handler(message)
    message.reply.assert_called_with("Укажите название категории, например:\n/del кафе", reply_markup=handlers.menu_inline_keyboard())

@pytest.mark.asyncio
@patch("bot.handlers.categories.get_async_session")
@patch("bot.handlers.categories.get_context", new_callable=AsyncMock)
async def test_list_categories_handler_empty(get_context_mock, get_async_session_mock):
    message = MagicMock()
    message.text = "/categories"
    message.reply = AsyncMock()
    message.chat.id = 123
    message.chat.type = "group"

    session = MagicMock()
    session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(all=MagicMock(return_value=[])))))
    get_async_session_mock.return_value.__aenter__.return_value = session
    get_context_mock.return_value = MagicMock(id=1)

    await handlers.list_categories_handler(message)
    message.reply.assert_called_with("В этом чате нет доступных категорий.", reply_markup=handlers.menu_inline_keyboard())
