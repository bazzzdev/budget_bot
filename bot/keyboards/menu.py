from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup


def menu_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[[InlineKeyboardButton(text="Меню", callback_data="main_menu")]]
    )


def submenu_inline_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [InlineKeyboardButton(text="Категории", callback_data="show_categories")],
            [InlineKeyboardButton(text="Статистика", callback_data="statistics_menu")],
            [InlineKeyboardButton(text="Команды", callback_data="show_commands")],
            [InlineKeyboardButton(text="Помощь", callback_data="show_help")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")],
        ]
    )


def statistics_menu_keyboard():
    return InlineKeyboardMarkup(
        inline_keyboard=[
            [
                InlineKeyboardButton(
                    text="По категориям", callback_data="stat_by_category"
                )
            ],
            [InlineKeyboardButton(text="Детализация", callback_data="stat_detail")],
            [InlineKeyboardButton(text="Назад", callback_data="back_to_menu")],
        ]
    )


def period_menu_keyboard(prefix: str, days=True, weeks=True, months=True):
    buttons = []
    if days:
        buttons.append(
            [InlineKeyboardButton(text="День", callback_data=f"{prefix}_day")]
        )
    if weeks:
        buttons.append(
            [InlineKeyboardButton(text="Неделя", callback_data=f"{prefix}_week")]
        )
    if months:
        buttons.append(
            [InlineKeyboardButton(text="Месяц", callback_data=f"{prefix}_month")]
        )
    buttons.append(
        [InlineKeyboardButton(text="Назад", callback_data="statistics_menu")]
    )
    return InlineKeyboardMarkup(inline_keyboard=buttons)
