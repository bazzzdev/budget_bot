from .base_commands import router as base_commands_router
from .categories import router as categories_router
from .finance import router as finance_router
from .menu import router as menu_router
from .statistics import router as stat_router

all_handlers = [
    base_commands_router,
    menu_router,
    categories_router,
    stat_router,
    finance_router,
]