from datetime import UTC
from unittest.mock import AsyncMock, patch, MagicMock

import pytest

from bot.handlers import statistics


@pytest.mark.asyncio
@patch("bot.handlers.statistics.get_async_session")
@patch("bot.handlers.statistics.get_or_create_context", new_callable=AsyncMock)
@patch("bot.handlers.statistics.get_user", new_callable=AsyncMock)
@patch("bot.handlers.statistics.parse_date_arg")
async def test_statcat_handler_success(parse_date_arg_mock, get_user_mock, get_context_mock, get_async_session_mock):
    parse_date_arg_mock.return_value = ("2024-01-01", "2024-01-02", "день")
    message = AsyncMock()
    callback = MagicMock()
    callback.message = message
    callback.from_user.id = 1
    message.chat = MagicMock()
    session = AsyncMock()
    session.execute = AsyncMock(side_effect=[
        MagicMock(all=MagicMock(return_value=[("Зарплата", 1000)])),  # Доходы по категориям
        MagicMock(all=MagicMock(return_value=[("Еда", 500)])),        # Расходы по категориям
    ])
    get_async_session_mock.return_value.__aenter__.return_value = session
    get_context_mock.return_value = MagicMock(id=1)
    get_user_mock.return_value = MagicMock(id=1)
    await statistics.statcat_handler(callback, "day")
    message.answer.assert_awaited()
    assert "Зарплата" in message.answer.call_args[0][0]
    assert "Еда" in message.answer.call_args[0][0]

@pytest.mark.asyncio
@patch("bot.handlers.statistics.get_async_session")
@patch("bot.handlers.statistics.get_or_create_context", new_callable=AsyncMock)
@patch("bot.handlers.statistics.get_user", new_callable=AsyncMock)
async def test_statdetail_handler_success(get_user_mock, get_context_mock, get_async_session_mock):
    message = AsyncMock()
    callback = MagicMock()
    callback.message = message
    callback.from_user.id = 1
    message.chat = MagicMock()
    now = statistics.datetime.now(UTC)
    # Мокаем execute для доходов и расходов
    session = AsyncMock()
    session.execute = AsyncMock(side_effect=[
        MagicMock(all=MagicMock(return_value=[(now, 1000, "Зарплата")])),  # Доходы
        MagicMock(all=MagicMock(return_value=[(now, 500, "Еда")])),        # Расходы
    ])
    get_async_session_mock.return_value.__aenter__.return_value = session
    get_context_mock.return_value = MagicMock(id=1)
    get_user_mock.return_value = MagicMock(id=1)
    await statistics.statdetail_handler(callback, None)
    message.answer.assert_awaited()
    assert "Зарплата" in message.answer.call_args[0][0]
    assert "Еда" in message.answer.call_args[0][0]
