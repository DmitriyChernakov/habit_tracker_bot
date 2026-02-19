import asyncio
import logging
from aiogram import Bot, Dispatcher
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand

from config import BOT_TOKEN
from handlers import common, habits


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
dp.include_router(habits.router)


async def set_commands(bot: Bot):
    """Sets the list of commands for the bot's menu"""
    commands = [
        BotCommand(command="start", description="🚀 Запустить бота"),
        BotCommand(command="add", description="➕ Добавить привычку"),
        BotCommand(command="today", description="📅 Привычки на сегодня"),
        BotCommand(command="help", description="❓ Помощь"),
        BotCommand(command="cancel", description="✖ Отменить действие"),
    ]
    await bot.set_my_commands(commands=commands)


async def main():
    """The main function of launching the bot"""
    logging.info("Bot starting...")

    await set_commands(bot)
    logging.info("The command menu is set")

    await dp.start_polling(bot)


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("Bot shuts down...")
