from database import postgres_db
import logging
from aiogram import Dispatcher, executor
from create_bot import dp, bot, scheduler
from utils.set_bot_commands import set_default_commands
from handlers import client, admin
from data.config import *


postgres_db.sql_start()
client.register_handlers_client(dp)
admin.register_handlers_admin(dp)


async def on_startup(dp: Dispatcher):
    if APP_NAME:
        await bot.set_webhook(WEBHOOK_URL, drop_pending_updates=True)
        await set_default_commands(dp)
        scheduler.start()
    scheduler.add_job(postgres_db.no_mark_lst, "interval", days=2, args=(dp,))
    logging.warning('Starting connection!!!!!!')



async def on_shutdown(dp: Dispatcher):
    if APP_NAME:
        await bot.delete_webhook()
    logging.warning('Ending connection')
    postgres_db.base.close()


def poll():
    ''' The bot is started by the main method. '''
    scheduler.start()
    executor.start_polling(dp, on_startup=on_startup, skip_updates=True)


def webhook():
    ''' Webhook connection. '''
    from data.config import WEBHOOK_PATH, WEBAPP_PORT, WEBAPP_HOST
    executor.start_webhook(
        dispatcher=dp,
        webhook_path=WEBHOOK_PATH,
        on_startup=on_startup,
        on_shutdown=on_shutdown,
        skip_updates=True,
        host=WEBAPP_HOST,
        port=WEBAPP_PORT,
    )
