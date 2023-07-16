import os
import sys
import colorama
from aiogram import executor, Dispatcher
from kodex.data.config import get_admins
from kodex.data.loader import scheduler
from kodex.handlers import dp
from kodex.middlewares import setup_middlewares
from kodex.services.api_session import AsyncSession
from kodex.services.api_sqlite import create_dbx
from kodex.utils.misc.bot_commands import set_commands
from kodex.utils.misc.bot_filters import IsPrivate
from kodex.utils.misc.bot_logging import bot_logger
from kodex.utils.misc_functions import (check_update, check_bot_data, startup_notify, update_profit_day,
                                        update_profit_week, autobackup_admin, check_mail)

colorama.init()


async def scheduler_start(kodex_one):
    scheduler.add_job(update_profit_day, trigger="cron", hour=00)
    scheduler.add_job(update_profit_week, trigger="cron", day_of_week="mon", hour=00, minute=1)
    scheduler.add_job(autobackup_admin, trigger="cron", hour=00)
    scheduler.add_job(check_update, trigger="cron", hour=00, args=(kodex_one,))
    scheduler.add_job(check_mail, trigger="cron", hour=12, args=(kodex_one,))


async def on_startup(dp: Dispatcher):
    kodex_one = AsyncSession()
    dp.bot['kodex_one'] = kodex_one

    await dp.bot.delete_webhook()
    await dp.bot.get_updates(offset=-1)

    await set_commands(dp)
    await check_bot_data()
    await scheduler_start(kodex_one)
    await startup_notify(dp, kodex_one)

    bot_logger.warning("Kodex Technologies")
    print(colorama.Fore.LIGHTRED_EX + f"The bot is running - @{(await dp.bot.get_me()).username} ")
    print(colorama.Fore.LIGHTWHITE_EX + "TG developer - @delormen")
    print(colorama.Fore.RESET)

    if len(get_admins()) == 0: print("***** ENTER ADMIN ID IN settings.ini *****")


# Выполнение функции после выключения бота
async def on_shutdown(dp: Dispatcher):
    kodex_one: AsyncSession = dp.bot['kodex_one']
    await kodex_one.close()

    await dp.storage.close()
    await dp.storage.wait_closed()
    await (await dp.bot.get_session()).close()

    if sys.platform.startswith("win"):
        os.system("cls")
    else:
        os.system("clear")


if __name__ == "__main__":
    create_dbx()

    scheduler.start()
    dp.filters_factory.bind(IsPrivate)  # Подключение фильтра приватности
    setup_middlewares(dp)  # Подключение миддлварей

    executor.start_polling(dp, on_startup=on_startup, on_shutdown=on_shutdown)
