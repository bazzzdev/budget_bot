from unittest.mock import AsyncMock, MagicMock

import pytest

import bot.handlers.finance as finance


@pytest.mark.asyncio
async def test_handle_expense_income_valid_expense(mocker):
    message = AsyncMock()
    message.text = "1000 еда"
    message.from_user = MagicMock(id=1, username="testuser", first_name="Test")
    message.chat = MagicMock(id=123, type="private")
    message.reply = AsyncMock()
    message.answer = AsyncMock()

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    mocker.patch("bot.handlers.finance.get_or_create_user", new=AsyncMock(return_value=MagicMock(id=1)))
    mocker.patch("bot.handlers.finance.get_or_create_context", new=AsyncMock(return_value=MagicMock(id=1)))
    mocker.patch("bot.handlers.finance.get_category", new=AsyncMock(return_value=MagicMock(id=1, title="еда")))
    mocker.patch("bot.handlers.finance.Expense", autospec=True)
    mocker.patch("bot.handlers.finance.datetime", wraps=finance.datetime)
    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_session), __aexit__=AsyncMock()))

    await finance.handle_expense_income(message)
    message.answer.assert_awaited()
    assert mock_session.add.call_count == 1
    assert mock_session.commit.await_count == 1

@pytest.mark.asyncio
async def test_handle_expense_income_invalid_format(mocker):
    message = AsyncMock()
    message.text = "еда 1000"
    message.reply = AsyncMock()
    message.answer = AsyncMock()
    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(__aenter__=AsyncMock(), __aexit__=AsyncMock()))
    await finance.handle_expense_income(message)
    message.reply.assert_not_awaited()
    message.answer.assert_not_awaited()

@pytest.mark.asyncio
async def test_delete_record_callback_not_author(mocker):
    callback = AsyncMock()
    callback.data = "delete_expense:1"
    callback.from_user = MagicMock(id=2)
    callback.answer = AsyncMock()
    callback.message = AsyncMock()

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=MagicMock(user_id=1))
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=MagicMock(id=3))))))

    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_session), __aexit__=AsyncMock()))

    await finance.delete_record_callback(callback)
    callback.answer.assert_awaited_with("Вы не можете удалить эту запись.", show_alert=True)

@pytest.mark.asyncio
async def test_delete_record_callback_success(mocker):
    callback = AsyncMock()
    callback.data = "delete_income:1"
    callback.from_user = MagicMock(id=1)
    callback.answer = AsyncMock()
    callback.message = AsyncMock()

    mock_session = AsyncMock()
    mock_session.get = AsyncMock(return_value=MagicMock(user_id=1))
    mock_session.execute = AsyncMock(return_value=MagicMock(scalars=MagicMock(return_value=MagicMock(first=MagicMock(return_value=MagicMock(id=1))))))
    mock_session.delete = AsyncMock()
    mock_session.commit = AsyncMock()

    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_session), __aexit__=AsyncMock()))

    await finance.delete_record_callback(callback)
    callback.message.edit_text.assert_awaited_with("Запись удалена.")
    callback.answer.assert_awaited()
    assert mock_session.delete.await_count == 1
    assert mock_session.commit.await_count == 1

@pytest.mark.asyncio
async def test_handle_expense_income_valid_income(mocker):
    message = AsyncMock()
    message.text = "+5000 зарплата"
    message.from_user = MagicMock(id=1, username="testuser", first_name="Test")
    message.chat = MagicMock(id=123, type="private")
    message.reply = AsyncMock()
    message.answer = AsyncMock()

    mock_session = AsyncMock()
    mock_session.add = MagicMock()
    mock_session.commit = AsyncMock()

    mocker.patch("bot.handlers.finance.get_or_create_user", new=AsyncMock(return_value=MagicMock(id=1)))
    mocker.patch("bot.handlers.finance.get_or_create_context", new=AsyncMock(return_value=MagicMock(id=1)))
    mocker.patch("bot.handlers.finance.get_category", new=AsyncMock(return_value=MagicMock(id=1, title="зарплата")))
    mocker.patch("bot.handlers.finance.Income", autospec=True)
    mocker.patch("bot.handlers.finance.datetime", wraps=finance.datetime)
    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(__aenter__=AsyncMock(return_value=mock_session), __aexit__=AsyncMock()))

    await finance.handle_expense_income(message)
    message.answer.assert_awaited()
    assert mock_session.add.call_count == 1
    assert mock_session.commit.await_count == 1
