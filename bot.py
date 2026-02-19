import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage

from config import BOT_TOKEN
from handlers import common


# Configuring logging
logging.basicConfig(level=logging.INFO)

# Creating bot
bot = Bot(token=BOT_TOKEN)

# FSM (Finite State Machine) state Storage - useful for dialogues
storage = MemoryStorage()

# Dispatcher - receives updates from Telegram and forwards them to the necessary handlers.
dp = Dispatcher(storage=storage)

# Connecting router (command handler)
dp.include_router(common.router)


async def main():
    """The main function of launching the bot"""
    logging.info("Bot starting...")
    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shuts down...")
