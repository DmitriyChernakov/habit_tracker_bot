from aiogram import Router
from aiogram.filters import CommandStart, Command
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

    # In /start show a list of commands
    await show_commands(message, is_welcome=True)


@router.message(Command("help"))
async def cmd_help(message: Message):
    """Show the list of available commands"""
    await show_commands(message)


async def show_commands(message: Message, is_welcome: bool = False):
    """A common function for displaying commands"""
    welcome_text = "👋 Привет! Я помогу тебе формировать полезные привычки.\n\n" if is_welcome else ""

    commands_text = (
        f"{welcome_text}"
        "📋 **Доступные команды:**\n\n"
        "🚀 **Основные**\n"
        "/add - Добавить новую привычку\n\n"
        "⚙ **Другое**\n"
        "/help - Показать это сообщение\n"
        "/cancel - Отменить текущее действие\n\n"
        "💡 **Совет**: Можно в любой момент отменить добавление привычки командой /cancel"
    )

    await message.answer(commands_text, parse_mode="Markdown")
