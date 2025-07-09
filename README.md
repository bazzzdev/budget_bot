# SmartSpends Bot

Telegram-бот для учета личных и групповых расходов/доходов. Позволяет вести учет финансов как в личных сообщениях, так и в групповых чатах.

## Основной функционал

- Учет доходов и расходов по категориям
- Просмотр статистики за день/неделю/месяц
- Детализация операций
- Управление категориями (добавление/удаление)
- Поддержка групповых чатов
- Инлайн-клавиатура для удобной навигации

## Основные команды

- `+сумма категория` - добавить доход (например: `+5000 зарплата`)
- `сумма категория` - добавить расход (например: `1000 кафе`) 
- `/stat day|week|month|DD.MM.YYYY|DD.MM.YYYY - DD.MM.YYYY` - показать статистику
- `/statcat day|week|month|DD.MM.YYYY|DD.MM.YYYY - DD.MM.YYYY` - статистика по категориям
- `/statdetail day` - детализация операций за день
- `/categories` - список доступных категорий
- `/add категория` - добавить категорию (только для админов в группе)
- `/del категория` - удалить категорию (только для админов в группе)
- `/clearcontext` - очистить все данные чата (только для админов в группе)
- `/commands` - список всех команд
- `/help` - помощь

## Технологии

- Python 3.11+
- aiogram 3.21
- SQLAlchemy 2.0
- alembic
- pytest
- loguru

## Установка и запуск

1. Клонируйте репозиторий
2. Установите зависимости:
```bash
pip install -r requirements.txt
```
3. Установите PostgreSQL и создайте пользователя и базу данных:
```bash
sudo apt install postgresql postgresql-contrib
```
```bash
# Замените `your_user`, `your_password` и `your_db` на ваши значения
sudo -u postgres psql -c "CREATE USER your_user WITH PASSWORD 'your_password'; CREATE DATABASE your_db OWNER your_user; GRANT ALL PRIVILEGES ON DATABASE your_db TO your_user;"
```

4. Создайте .env файл в корне проекта и укажите переменные окружения:
```env
BOT_TOKEN=your_bot_token
DATABASE_URL=postgresql+asyncpg://your_user:your_password@localhost:5432/your_db
```
5. Примените миграции базы данных:
```bash
alembic upgrade head
```
6. Запустите бота:
```bash
python main.py
```

## Тестирование
Для запуска тестов используйте команду:
```bash
pytest
```
## Лицензия
**MIT**

## Автор.
@bazzzvl