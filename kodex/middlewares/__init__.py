
from aiogram import Dispatcher

from kodex.middlewares.exists_user import ExistsUserMiddleware
from kodex.middlewares.throttling import ThrottlingMiddleware


# Подключение милдварей
def setup_middlewares(dp: Dispatcher):
    dp.middleware.setup(ExistsUserMiddleware())
    dp.middleware.setup(ThrottlingMiddleware())
