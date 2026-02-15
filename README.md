# budget_bot

## Описание
Telegram-бот для учета личных и групповых расходов/доходов (SmartSpends Bot).

## Репозиторий
- GitHub: git@github.com:bazzzdev/budget_bot.git
- Рабочая ветка: master

## Стек
- Python
- Docker

## Быстрый старт
1. Установить зависимости:
   pip install -r requirements.txt
2. Создать .env с BOT_TOKEN и DATABASE_URL.
3. Применить миграции:
   alembic upgrade head
4. Запустить бота:
   python main.py

## Структура
- bot/
- alembic/

## Полезные команды
```bash
python main.py
alembic upgrade head
pytest
```

## Статус
Активный

## Лицензия
Не указана
