from aiogram import Bot, types, Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

from data.config import API_TOKEN
from apscheduler.schedulers.asyncio import AsyncIOScheduler

storage = MemoryStorage()
bot = Bot(token=API_TOKEN, parse_mode=types.ParseMode.HTML)
dp = Dispatcher(bot, storage=storage)
scheduler = AsyncIOScheduler()

