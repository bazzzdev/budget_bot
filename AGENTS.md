# Repository Guidelines

## Project Structure & Module Organization
- `main.py`: bot entrypoint; registers routers and starts polling.
- `bot/handlers/`: Telegram command/message handlers (`finance.py`, `categories.py`, `statistics.py`, etc.).
- `bot/services/`: database session and domain helpers.
- `bot/models/`: SQLAlchemy models and base classes.
- `bot/keyboards/`: reply/inline keyboard builders.
- `bot/tests/`: pytest suite for handler behavior and business logic.
- `alembic/` and `alembic.ini`: migration environment and versioned schema changes.
- Runtime config is loaded from `.env` (see `.env.example`).

## Build, Test, and Development Commands
- `pip install -r requirements.txt`: install project dependencies.
- `alembic upgrade head`: apply the latest DB schema locally.
- `python main.py`: run the bot in polling mode.
- `pytest`: run all tests (CI runs this on pushes to `master`).
- `docker compose up -d --build`: start bot and Postgres in containers.
- `docker compose down`: stop local containers.

## Coding Style & Naming Conventions
- Follow PEP 8 with 4-space indentation and `snake_case` for functions and variables.
- Keep handlers focused: parse input, then delegate DB/business operations to `bot/services/`.
- Use descriptive module names by feature (`finance`, `categories`, `statistics`).
- Prefer explicit imports and short, readable async functions.
- Keep user-facing text consistent with the existing Russian-language message style.

## Testing Guidelines
- Frameworks: `pytest`, `pytest-asyncio`, `pytest-mock`.
- Store tests in `bot/tests/` and name files `test_<feature>.py`.
- Name tests by behavior, for example `test_handle_expense_income_valid_income`.
- For bot logic changes, add or adjust async tests and run `pytest` before opening a PR.

## Commit & Pull Request Guidelines
- Commit history uses short prefixes like `Fix:` and `docs:`; keep messages imperative and scoped.
- Recommended commit format: `<type>: <brief summary>` (example: `Fix: validate amount parsing`).
- PRs should clearly state what changed and why.
- PRs should link the related issue/task when available.
- PRs touching `alembic/versions/` should include migration notes.
- PRs should include test evidence (for example, `pytest` output summary).

## Security & Configuration Tips
- Never commit real secrets; store tokens and passwords only in `.env`.
- Required variables include `BOT_TOKEN`, `DATABASE_URL`, and Postgres credentials used in `docker-compose.yml`.
