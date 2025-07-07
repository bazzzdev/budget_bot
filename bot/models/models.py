from datetime import datetime
from decimal import Decimal

from sqlalchemy import (
    BigInteger,
    ForeignKey,
    func,
)
from sqlalchemy.orm import Mapped, mapped_column

from bot.models.base import Base


class User(Base):
    """
    Модель пользователя Telegram.
    """
    __tablename__ = "users"

    id: Mapped[int] = mapped_column(primary_key=True)
    tg_id: Mapped[int] = mapped_column(BigInteger, unique=True)  # Telegram user ID
    username: Mapped[str] = mapped_column(nullable=True)         # Username в Telegram
    first_name: Mapped[str] = mapped_column(nullable=True)       # Имя пользователя

class Context(Base):
    """
    Модель контекста (чат или пользователь).
    """
    __tablename__ = "contexts"

    id: Mapped[int] = mapped_column(primary_key=True)
    context_id: Mapped[int] = mapped_column(BigInteger, index=True)  # chat_id или user_id
    context_type: Mapped[str] = mapped_column()                      # 'private' или 'group'

class Category(Base):
    """
    Модель категории дохода или расхода.
    """
    __tablename__ = "categories"

    id: Mapped[int] = mapped_column(primary_key=True)
    title: Mapped[str] = mapped_column()                                 # Название категории
    context_id: Mapped[int] = mapped_column(ForeignKey("contexts.id"))   # Контекст (чат)
    is_default: Mapped[bool] = mapped_column(default=False)              # Является ли категорией по умолчанию
    is_deleted: Mapped[bool] = mapped_column(default=False)              # Удалена ли категория

class Expense(Base):
    """
    Модель расхода пользователя.
    """
    __tablename__ = "expenses"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))            # Пользователь
    context_id: Mapped[int] = mapped_column(ForeignKey("contexts.id"))      # Контекст (чат)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))   # Категория расхода
    amount: Mapped[Decimal] = mapped_column()                               # Сумма расхода
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # Дата и время создания

class Income(Base):
    """
    Модель дохода пользователя.
    """
    __tablename__ = "incomes"

    id: Mapped[int] = mapped_column(primary_key=True)
    user_id: Mapped[int] = mapped_column(ForeignKey("users.id"))            # Пользователь
    context_id: Mapped[int] = mapped_column(ForeignKey("contexts.id"))      # Контекст (чат)
    category_id: Mapped[int] = mapped_column(ForeignKey("categories.id"))   # Категория дохода
    amount: Mapped[Decimal] = mapped_column()                               # Сумма дохода
    created_at: Mapped[datetime] = mapped_column(server_default=func.now()) # Дата и время создания