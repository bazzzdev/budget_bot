from unittest.mock import AsyncMock, MagicMock, patch

import pytest

import bot.handlers.base_commands as base_commands
from bot.handlers.base_commands import get_user_display  # если нужно, для патчинга

@pytest.mark.asyncio
@patch("bot.handlers.base_commands.menu_inline_keyboard", return_value=MagicMock())
@patch("bot.handlers.base_commands.get_context", new_callable=AsyncMock)
@patch("bot.handlers.base_commands.get_or_create_user", new_callable=AsyncMock)
@patch("bot.handlers.base_commands.AsyncSessionLocal")
@patch("bot.handlers.base_commands.get_user_display", side_effect=lambda user: user.first_name)
async def test_start_handler(mock_get_user_display, mock_session_local, mock_get_or_create_user, mock_get_context, mock_menu_keyboard):
    message = AsyncMock()
    message.from_user.first_name = "Вася"
    message.from_user.id = 123
    message.from_user.username = "testuser"
    message.chat.id = 456
    message.chat.type = "private"
    message.answer = AsyncMock()

    mock_session = AsyncMock()
    mock_session_local.return_value.__aenter__.return_value = mock_session

    await base_commands.start_handler(message)

    mock_get_or_create_user.assert_awaited_once_with(mock_session, message.from_user)
    mock_get_context.assert_awaited_once_with(mock_session, message.chat)
    message.answer.assert_awaited_once()

    sent_text = message.answer.call_args[0][0]
    assert "Привет, Вася" in sent_text
    assert "<b>Основные команды:</b>" in sent_text
    assert message.answer.call_args[1]['reply_markup'] is mock_menu_keyboard.return_value
