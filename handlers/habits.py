from aiogram import Router, F
from aiogram.types import Message, CallbackQuery
from aiogram.filters import Command, StateFilter
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder

from database import Database
from states import AddHabit

router = Router()
db = Database()

# Temp storage for habit data during a conversation
user_temp_data = {}


# Cancel command
@router.message(Command("cancel"))
async def cmd_cancel(message: Message, state: FSMContext):
    """Canceling the current action"""
    current_state = await state.get_state()
    if current_state is None:
        await message.answer("🤷 Нет активного действия для отмены.")
        return

    await state.clear()
    await message.answer("✅ Действие отменено. Можешь начать заново командой /add")


@router.message(Command("add"))
async def cmd_add(message: Message, state: FSMContext):
    """The process of adding a habit"""
    await state.set_state(AddHabit.waiting_for_name)
    await message.answer(
        "📝 Давй добавим новую привычку!\n\n"
        "Напиши название привычки. Например:\n"
        "▪ Выпить стакан воды\n"
        "▪ Сделать зарядку\n"
        "▪ Почитать 10 минут"
    )


@router.message(AddHabit.waiting_for_name, ~F.text.startswith('/'))
async def habit_name_received(message: Message, state: FSMContext):
    """Get the name of the habit and find out the time"""
    habit_name = message.text.strip()

    if len(habit_name) > 100:
        await message.answer("❌ Я бы назвал привычку немного короче (не более 100 символов).")
        return
    if len(habit_name) < 3:
        await message.answer("❌ Давай попробуем назвать привычку немного длиннее (не менее 3 символов).")
        return

    # Save the name to the temp storage
    await state.update_data(habit_name=habit_name)

    # Moving on to the next step
    await state.set_state(AddHabit.waiting_for_time)

    # Creating a keyboard with options
    keyboard = InlineKeyboardBuilder()
    keyboard.button(text="⏰ Без напоминания", callback_data="no_reminder")
    keyboard.button(text="🎯 Указать свое время", callback_data="custom_time")
    keyboard.adjust(1)  # One button in a row

    await message.answer(
        f"Отлично! Привычка: \"{habit_name}\"\n\n"
        "🕒 В какое время напомнить?",
        reply_markup=keyboard.as_markup()
    )


@router.callback_query(AddHabit.waiting_for_time, F.data == "no_reminder")
async def no_reminder_chosen(callback: CallbackQuery, state: FSMContext):
    """The user selected 'no reminder'"""
    await callback.answer()  # Close the watch on the button

    # Getting the saved data
    data = await state.get_data()
    habit_name = data.get('habit_name')
    user_id = callback.from_user.id

    # Saving a habit in the DB without time
    db.add_habit(user_id, habit_name)

    # Ending FSM
    await state.clear()

    await callback.message.edit_text(
        f"✅ Привычка \"{habit_name}\" добавлена!\n\n"
        f"Напоминаний не будет. Чтобы отметить выполнение, используй /today"
    )


@router.callback_query(AddHabit.waiting_for_time, F.data == "custom_time")
async def custom_time_chosen(callback: CallbackQuery, state: FSMContext):
    """The user specified his time"""
    await callback.answer()
    await callback.message.edit_text(
        "⌚ Напишите время в формате ЧЧ:ММ (например, 09:00 или 21:00)\n\n"
        "Я буду присылать тебе напоминания каждый день в это время."
    )
    # Remain in the same state (waiting_for_time) but now waiting for the text with the time


@router.message(AddHabit.waiting_for_time, ~F.text.startswith('/'))
async def habit_time_received(message: Message, state: FSMContext):
    """Getting the time from user"""
    time_text = message.text.strip()

    # Checking the time format
    if ':' not in time_text:
        await message.answer("❌ Используй двоеточие между часами и минутами. Пример: 09:30")
        return

    # Divide into parts
    parts = time_text.split(':')
    if len(parts) != 2:
        await message.answer("❌ Время должно состоять из двух частей: часы и минуты. Пример: 09:30")
        return

    # Checking that both parts can be converted to numbers.
    try:
        hours = int(parts[0])
        minutes = int(parts[1])
    except ValueError:
        await message.answer("❌ Часы и минуты должны быть числами. Пример: 09:30")
        return

    # Checking the ranges
    if not (0 <= hours <= 23):
        await message.answer("❌ Часы должны быть от 0 до 23")
        return

    if not (0 <= minutes <= 59):
        await message.answer("❌ Минуты должны быть от 0 до 59")
        return

    # Formatting the time for the DB
    reminder_time = f"{hours:02d}:{minutes:02d}"

    # Getting the habit name
    data = await state.get_data()
    habit_name = data.get('habit_name')
    user_id = message.from_user.id

    # Saving a habit in the DB
    db.add_habit(user_id, habit_name, reminder_time)

    # Ending FSM
    await state.clear()

    await message.answer(
        f"✅ Привычка \"{habit_name}\" добавлена!\n\n"
        f"🕒 Напоминание каждый день в {reminder_time}\n\n"
        "Чтобы отметить выполнение, используй /today"
    )
