version: '3.9'

services:
  bot:
    build: .
    container_name: telegram_bot
    restart: always
    env_file:
      - .env
    depends_on:
      - db
    command: >
      sh -c "alembic upgrade head &&
             python main.py"

  db:
    image: postgres:16
    container_name: postgres_db
    restart: always
    environment:
      POSTGRES_USER: ${POSTGRES_USER}
      POSTGRES_PASSWORD: ${POSTGRES_PASSWORD}
      POSTGRES_DB: ${POSTGRES_DB}
    volumes:
      - postgres_data:/var/lib/postgresql/data
    ports:
      - "5432:5432"

volumes:
  postgres_data:
