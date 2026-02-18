import sqlite3
import datetime


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
