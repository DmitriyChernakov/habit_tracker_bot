from aiogram.fsm.state import State, StatesGroup


class AddHabit(StatesGroup):
    """States for the habit addition process"""

    # Waiting the name of the habit
    waiting_for_name = State()

    # Waiting for the reminder time
    waiting_for_time = State()
