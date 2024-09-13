import asyncio

from aiogram import Bot, Dispatcher
from aiogram.methods import DeleteWebhook

import config
import handlers

TOKEN = config.get("TOKEN")
SERVER_URL = config.get("SERVER_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(handlers.router)
    await bot(DeleteWebhook(drop_pending_updates=True))
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())