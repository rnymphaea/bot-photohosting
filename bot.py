import asyncio

from aiogram import Bot, Dispatcher

import config
import handlers

TOKEN = config.get("TOKEN")
SERVER_URL = config.get("SERVER_URL")

bot = Bot(token=TOKEN)
dp = Dispatcher()


async def main():
    dp.include_routers(handlers.router)
    await dp.start_polling(bot)

if __name__ == '__main__':
    asyncio.run(main())
