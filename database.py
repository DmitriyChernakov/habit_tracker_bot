import sqlite3
from datetime import date


class Database:
    def __init__(self, db_path="habits.db"):
        self.db_path = db_path
        self.init_db()

    def get_connection(self):
        """Create DB connection"""
        return sqlite3.connect(self.db_path)

    def init_db(self):
        """Create tables if there are none"""
        with self.get_connection() as conn:
            cursor = conn.cursor()

            # Users table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS users (
                    user_id INTEGER PRIMARY KEY,
                    username TEXT,
                    first_name TEXT,
                    last_name TEXT,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    timezone TEXT DEFAULT 'Europe/Moscow'
                )
            """)

            # Habits table
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS habits (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER,
                    name TEXT NOT NULL,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    reminder_time TEXT,
                    FOREIGN KEY (user_id) REFERENCES users (user_id)
                )
            """)

            # Table of completion marks
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS checkins (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    habit_id INTEGER,
                    check_date DATE DEFAULT CURRENT_DATE,
                    completed BOOLEAN DEFAULT 1,
                    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                    FOREIGN KEY (habit_id) REFERENCES habits (id) ON DELETE CASCADE,
                    UNIQUE(habit_id, check_date)
                )
            """)

            conn.commit()

    def add_user(self, user_id, username, first_name, last_name):
        """Adds a new user or updates an existing one"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, created_at)
                VALUES (?, ?, ?, ?, CURRENT_TIMESTAMP)
            """, (user_id, username, first_name, last_name))
            conn.commit()

    def add_habit(self, user_id, habit_name, reminder_time=None):
        """Ads a new habit"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                INSERT INTO habits (user_id, name, reminder_time)
                VALUES (?, ?, ?)
            """, (user_id, habit_name, reminder_time))
            conn.commit()
            return cursor.lastrowid  # Returning the ID of the created habit

    def get_user_habits(self, user_id):
        """Returns all the user's habits"""
        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT id, name, reminder_time, created_at
                FROM habits
                WHERE user_id = ?
                ORDER BY created_at DESC
            """, (user_id,))
            return cursor.fetchall()


    def get_habits_with_today_status(self, user_id):
        """
        Return all the user's habits with information about whether they are completed today
        """
        today = date.today().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                SELECT
                    h.id,
                    h.name,
                    h.reminder_time,
                    CASE WHEN c.id IS NOT NULL THEN 1 ELSE 0 END as completed_today
                FROM habits h
                LEFT JOIN checkins c ON h.id = c.habit_id AND c.check_date = ?
                WHERE h.user_id = ?
                ORDER BY
                    completed_today ASC,  -- unfulfilled from above
                    h.reminder_time IS NULL,  -- with the reminder above
                    h.reminder_time ASC
            """, (today, user_id))

            return cursor.fetchall()


    def mark_habit_completed(self, habit_id):
        """
        Marks a habit as completed today.
        Returns 'True' if the mark ha been created, 'False' if it has already been
        """
        today = date.today().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            try:
                cursor.execute("""
                    INSERT INTO checkins (habit_id, check_date)
                    VALUES (?, ?)
                """, (habit_id, today))
                conn.commit()
                return True
            except sqlite3.IntegrityError:
                # Already mark today
                return False


    def unmark_today(self, habit_id):
        """Deletes the completion mark for today"""
        today = date.today().isoformat()

        with self.get_connection() as conn:
            cursor = conn.cursor()
            cursor.execute("""
                DELETE FROM checkins
                WHERE habit_id = ? AND check_date = ?
            """, (habit_id, today))
            conn.commit()
            return cursor.rowcount > 0
