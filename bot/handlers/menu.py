from aiogram import Router, types
from aiogram.types import CallbackQuery

from bot.handlers.categories import list_categories_handler
from bot.handlers.statistics import statcat_handler, statdetail_handler
from bot.handlers.base_commands import commands_handler, help_handler
from bot.keyboards.menu import (
    menu_inline_keyboard,
    period_menu_keyboard,
    statistics_menu_keyboard,
    submenu_inline_keyboard,
)

router = Router()


@router.callback_query(lambda c: c.data == "main_menu")
async def show_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=submenu_inline_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "back_to_menu")
async def back_to_main_menu(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=menu_inline_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "show_categories")
async def show_categories_callback(callback: types.CallbackQuery):
    await list_categories_handler(callback.message)
    await callback.answer()


@router.callback_query(lambda c: c.data == "statistics_menu")
async def show_statistics_menu(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(reply_markup=statistics_menu_keyboard())
    await callback.answer()


@router.callback_query(lambda c: c.data == "stat_by_category")
async def show_period_menu(callback: types.CallbackQuery):
    prefix = callback.data
    await callback.message.edit_reply_markup(reply_markup=period_menu_keyboard(prefix))
    await callback.answer()


@router.callback_query(lambda c: c.data == "stat_detail")
async def show_detail_period_menu(callback: types.CallbackQuery):
    await callback.message.edit_reply_markup(
        reply_markup=period_menu_keyboard("stat_detail", weeks=False, months=False)
    )
    await callback.answer()


@router.callback_query(lambda c: c.data == "stat_detail_day")
async def handle_stat_detail_day(callback: CallbackQuery):
    await callback.answer()
    await statdetail_handler(callback, None)


@router.callback_query(
    lambda c: c.data
    in ["stat_by_category_day", "stat_by_category_week", "stat_by_category_month"]
)
async def handle_stat_by_category_period(callback: CallbackQuery):
    period = callback.data.split("_")[-1]
    await callback.answer()
    await statcat_handler(callback, period)


@router.callback_query(lambda c: c.data == "show_commands")
async def show_commands_callback(callback: types.CallbackQuery):
    await commands_handler(callback.message)
    await callback.answer()

@router.callback_query(lambda c: c.data == "show_help")
async def show_help_callback(callback: types.CallbackQuery):
    await help_handler(callback.message)
    await callback.answer()
