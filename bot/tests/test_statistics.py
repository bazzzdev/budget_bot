from datetime import UTC
from unittest.mock import AsyncMock, patch, MagicMock, PropertyMock

import pytest

from bot.handlers import statistics


@pytest.mark.asyncio
@patch("bot.handlers.statistics.get_async_session")
@patch("bot.handlers.statistics.get_or_create_context", new_callable=AsyncMock)
@patch("bot.handlers.statistics.get_user", new_callable=AsyncMock)
@patch("bot.handlers.statistics.menu_inline_keyboard")
async def test_statdetail_handler_success(menu_kb_mock, get_user_mock, get_context_mock, get_async_session_mock):
    # Подготовка данных
    now = statistics.datetime.now(UTC)
    menu_kb_mock.return_value = MagicMock()

    # Создаем моки
    mock_message = AsyncMock()
    type(mock_message).chat = PropertyMock(return_value=MagicMock())

    callback = AsyncMock()
    type(callback).message = PropertyMock(return_value=mock_message)
    type(callback).from_user = PropertyMock(return_value=MagicMock(id=1, username="test_user"))

    # Настраиваем моки для сессии БД
    session = AsyncMock()
    session.execute.side_effect = [
        MagicMock(all=lambda: [(now, 1000, "Зарплата")]),  # Доходы
        MagicMock(all=lambda: [(now, 500, "Еда")]),        # Расходы
    ]

    # Настраиваем контекстный менеджер сессии
    get_async_session_mock.return_value.__aenter__.return_value = session
    get_context_mock.return_value = MagicMock(id=1)
    get_user_mock.return_value = MagicMock(id=1)

    # Вызываем тестируемую функцию
    await statistics.statdetail_handler(callback, None)

    # Проверяем результаты
    mock_message.answer.assert_called_once()
    call_args = mock_message.answer.call_args[0][0]
    assert "Зарплата" in call_args
    assert "Еда" in call_args
    assert "1000" in call_args
    assert "500" in call_args
    menu_kb_mock.assert_called_once()