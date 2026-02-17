from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from database import Database


router = Router()
db = Database()


@router.message(CommandStart())
async def cmd_start(message: Message):
    """Handler of the /start command"""
    user = message.from_user

    # Saving the user to the database
    db.add_user(
        user_id=user.id,
        username=user.username,
        first_name=user.first_name,
        last_name=user.last_name
    )

    # Sending a greeting
    await message.answer(
        f"👋 Привет, {user.first_name}!\n\n"
        "Я бот-трекер привычек. Помогу тебе формировать полезные привычки и следить за прогрессом.\n\n"
        "Пока я умею только здороваться, но скоро научусь большему! 🚀"
    )
