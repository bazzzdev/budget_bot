# AGENTS.md - Development Guide for SmartSpends Bot

## Project Overview
Telegram bot for tracking personal and group expenses/incomes using aiogram 3.21 and SQLAlchemy 2.0.

## Build/Test/Lint Commands

### Running Tests
```bash
# Run all tests
pytest

# Run specific test file
pytest bot/tests/test_finance.py

# Run single test function
pytest bot/tests/test_finance.py::test_handle_expense_income_valid_expense
```

### Database Operations
```bash
alembic upgrade head
alembic revision --autogenerate -m "description"
python main.py
```

## Code Style Guidelines

### Imports
- Group imports: standard library, third-party, then local modules
- Use absolute imports from project root: `from bot.models.models import User`
- Avoid wildcard imports

### Types and Type Hints
- Use Python 3.10+ union syntax with `|` operator
- All async functions must include return type hints
- Use SQLAlchemy 2.0 type hints: `Mapped[type]`

### Naming Conventions
- Functions: `snake_case`, Classes: `PascalCase`, Constants: `UPPER_SNAKE_CASE`
- Database tables: `snake_case`, Private methods: `_leading_underscore`

### Formatting
- 4 spaces for indentation
- Blank lines between top-level definitions (2 lines)
- Blank lines between logical sections (1 line)

### Error Handling
- Use try/except with specific exception types
- Return None or send user-friendly messages on errors
- Use logger for logging errors from loguru
- Always handle database commits with proper session management

```python
try:
    amount = Decimal(amount_str.replace(",", "."))
except (InvalidOperation, ValueError):
    await message.reply("Invalid amount")
    return
```

### Database Patterns
- Always use async context managers for sessions: `async with get_async_session() as session:`
- Use SQLAlchemy 2.0 select() for queries, not session.query()
- Always commit after changes: `await session.commit()`
- Use `.scalar_one_or_none()` or `.scalars().first()` for single results
- Use `ilike` for case-insensitive string matching

```python
async with get_async_session() as session:
    result = await session.execute(select(User).where(User.tg_id == tg_id))
    user = result.scalar_one_or_none()
```

### Handlers and Routers
- Use aiogram Router pattern: `router = Router()`
- Decorate handlers with filters: `@router.message(F.text)` or `@router.message(Command("start"))`
- Register all routers in `bot/handlers/__init__.py`
- Use `InlineKeyboardMarkup` for inline keyboards
- Parse mode is HTML by default (configured in settings.py)

### Logging
- Use loguru logger from `bot.utils.logger`
- Log important events at INFO level
- Log errors at appropriate levels
- Example: `logger.info(f"/start from user {message.from_user.id}")`

### Testing Patterns
- Use pytest-asyncio with `@pytest.mark.asyncio` decorator
- Mock bot interactions using `AsyncMock` and `AsyncMock`
- Use `mocker.patch` to patch dependencies
- Test files: `test_*.py` in `bot/tests/` directory
- Mock database sessions and operations
- Test return values and side effects separately

```python
@pytest.mark.asyncio
async def test_handle_expense_income_valid_expense(mocker):
    message = AsyncMock()
    message.text = "1000 food"
    message.reply = AsyncMock()
    
    mocker.patch("bot.handlers.finance.get_async_session", return_value=AsyncMock(...))
    
    await finance.handle_expense_income(message)
    message.answer.assert_awaited()
```

### Configuration
- Use pydantic BaseSettings for configuration
- Load environment variables with python-dotenv
- Store secrets in `.env` file (not committed)
- Reference `.env.example` for required variables

### Documentation
- Use docstrings for functions with triple quotes
- Docstrings are in Russian (matching codebase language)
- Describe function purpose and parameters briefly
- Keep docstrings concise and focused

```python
async def get_or_create_user(session, tg_user):
    """
    Gets or creates a user by Telegram ID.
    """
```

### Files Structure
- `main.py` - Entry point, register routers
- `bot/config.py` - Pydantic settings
- `bot/settings.py` - Bot and dispatcher setup
- `bot/handlers/` - Telegram message handlers
- `bot/models/` - SQLAlchemy ORM models
- `bot/services/` - Business logic and database helpers
- `bot/keyboards/` - Inline keyboard builders
- `bot/utils/` - Utilities (logger, etc.)
- `bot/tests/` - Test files

### Important Notes
- All database operations are async
- Use `Decimal` for monetary amounts (not float)
- Moscow timezone (UTC+3) is used for timestamps in handlers
- Categories are context-specific (per chat)
- Default categories are created for new chats
- Admin checks use `chat.get_member()` with try/except
- Use `get_user_display()` for consistent user display names
