import sqlite3
import datetime
from typing import Optional, List, Tuple, Dict, Any
import logging

logger = logging.getLogger(__name__)


class Database:
    def __init__(self, db_name: str = "class_bot.db"):
        self.db_name = db_name
        self.init_database()

    def get_connection(self):
        """Создает соединение с базой данных"""
        return sqlite3.connect(self.db_name, check_same_thread=False)

    def init_database(self):
        """Инициализирует таблицы базы данных"""
        conn = self.get_connection()
        cursor = conn.cursor()

        # Таблица для домашних заданий
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS homework
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           chat_id
                           INTEGER,
                           text
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')
        # Таблица для домашних заданий
        cursor.execute('''
                        CREATE TABLE IF NOT EXISTS ready_homework
                        (
                        id
                        INTEGER
                        PRIMARY
                        KEY
                        AUTOINCREMENT,
                        chat_id
                        INTEGER,
                        text
                        TEXT,
                        created_at
                        TIMESTAMP
                        DEFAULT
                        CURRENT_TIMESTAMP
                        )
                        ''')

        # Таблица для дежурных
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS duty
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           chat_id
                           INTEGER,
                           user1_id
                           INTEGER,
                           user1_name
                           TEXT,
                           user2_id
                           INTEGER,
                           user2_name
                           TEXT,
                           date
                           DATE,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица для расписания
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS schedule
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           chat_id
                           INTEGER,
                           text
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица для напоминаний
        #cursor.execute('''
                      # CREATE TABLE IF NOT EXISTS reminders
                      # (
                      #     id
                      #     INTEGER
                      #     PRIMARY
                      #     KEY
                      #     AUTOINCREMENT,
                      #     chat_id
                      #     INTEGER,
                      #     message
                       #    TEXT,
                       #    reminder_time
                       #    TIME,
                        #   job_id
                         #  TEXT,
                         #  created_at
                         #  TIMESTAMP
                         #  DEFAULT
                          # CURRENT_TIMESTAMP
                      # )
                     #  ''')

        # Таблица для архивации сообщений
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS messages
                       (
                           id
                           INTEGER
                           PRIMARY
                           KEY
                           AUTOINCREMENT,
                           message_id
                           INTEGER,
                           chat_id
                           INTEGER,
                           chat_type
                           TEXT,
                           user_id
                           INTEGER,
                           username
                           TEXT,
                           first_name
                           TEXT,
                           last_name
                           TEXT,
                           phone_number
                           TEXT,
                           photo_id
                           TEXT,
                           text
                           TEXT,
                           date
                           TIMESTAMP,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица для пользователей
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS users
                       (
                           user_id
                           INTEGER
                           PRIMARY
                           KEY,
                           username
                           TEXT,
                           first_name
                           TEXT,
                           last_name
                           TEXT,
                           phone_number
                           TEXT,
                           photo_id
                           TEXT,
                           last_seen
                           TIMESTAMP,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        # Таблица для чатов
        cursor.execute('''
                       CREATE TABLE IF NOT EXISTS chats
                       (
                           chat_id
                           INTEGER
                           PRIMARY
                           KEY,
                           chat_type
                           TEXT,
                           title
                           TEXT,
                           username
                           TEXT,
                           created_at
                           TIMESTAMP
                           DEFAULT
                           CURRENT_TIMESTAMP
                       )
                       ''')

        conn.commit()
        conn.close()

    # Homework methods
    def save_homework(self, chat_id: int, text: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO homework (chat_id, text) VALUES (?, ?)",
            (chat_id, text)
        )
        conn.commit()
        conn.close()

    def get_homework(self, chat_id: int) -> Optional[str]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM homework WHERE chat_id = ? ORDER BY created_at DESC LIMIT 1",
            (chat_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    #-------------------------------------------------------------------------------
    # Ready homework methods
    def save_ready_homework(self, chat_id: int, text: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO ready_homework (chat_id, text) VALUES (?, ?)",
            (chat_id, text)
        )
        conn.commit()
        conn.close()

    def get_ready_homework(self, chat_id: int) -> Optional[str]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM ready_homework WHERE chat_id = ? ORDER BY created_at DESC LIMIT 1",
            (chat_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None


    # Duty methods
    def save_duty(self, chat_id: int, user1_id: int, user1_name: str, user2_id: int, user2_name: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        # Удаляем старые записи для этого чата
        cursor.execute("DELETE FROM duty WHERE chat_id = ?", (chat_id,))
        cursor.execute(
            "INSERT INTO duty (chat_id, user1_id, user1_name, user2_id, user2_name, date) VALUES (?, ?, ?, ?, ?, DATE('now'))",
            (chat_id, user1_id, user1_name, user2_id, user2_name)
        )
        conn.commit()
        conn.close()

    def get_duty(self, chat_id: int) -> Optional[tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT user1_name, user2_name FROM duty WHERE chat_id = ? AND date = DATE('now')",
            (chat_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def clear_old_duty(self):
        """Очищает записи дежурных старше 1 дня"""
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM duty WHERE date < DATE('now')")
        conn.commit()
        conn.close()

    # Schedule methods
    def save_schedule(self, chat_id: int, text: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO schedule (chat_id, text) VALUES (?, ?)",
            (chat_id, text)
        )
        conn.commit()
        conn.close()

    def get_schedule(self, chat_id: int) -> Optional[str]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT text FROM schedule WHERE chat_id = ? ORDER BY created_at DESC LIMIT 1",
            (chat_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result[0] if result else None

    # Reminder methods
    def save_reminder(self, chat_id: int, message: str, reminder_time: str, job_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "INSERT INTO reminders (chat_id, message, reminder_time, job_id) VALUES (?, ?, ?, ?)",
            (chat_id, message, reminder_time, job_id)
        )
        conn.commit()
        conn.close()

    def get_reminder(self, job_id: str) -> Optional[tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute(
            "SELECT chat_id, message FROM reminders WHERE job_id = ?",
            (job_id,)
        )
        result = cursor.fetchone()
        conn.close()
        return result

    def delete_reminder(self, job_id: str):
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute("DELETE FROM reminders WHERE job_id = ?", (job_id,))
        conn.commit()
        conn.close()

    # Archive methods
    def save_message(self, message_data: Dict[str, Any]):
        conn = self.get_connection()
        cursor = conn.cursor()

        # Сохраняем пользователя
        cursor.execute('''
            INSERT OR REPLACE INTO users (user_id, username, first_name, last_name, phone_number, photo_id, last_seen)
            VALUES (?, ?, ?, ?, ?, ?, CURRENT_TIMESTAMP)
        ''', (
            message_data['user_id'],
            message_data['username'],
            message_data['first_name'],
            message_data['last_name'],
            message_data.get('phone_number'),
            message_data.get('photo_id')
        ))

        # Сохраняем чат
        cursor.execute('''
            INSERT OR REPLACE INTO chats (chat_id, chat_type, title, username)
            VALUES (?, ?, ?, ?)
        ''', (
            message_data['chat_id'],
            message_data['chat_type'],
            message_data.get('chat_title'),
            message_data.get('chat_username')
        ))

        # Сохраняем сообщение
        cursor.execute('''
                       INSERT INTO messages (message_id, chat_id, chat_type, user_id, username,
                                             first_name, last_name, phone_number, photo_id, text, date)
                       VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                       ''', (
                           message_data['message_id'],
                           message_data['chat_id'],
                           message_data['chat_type'],
                           message_data['user_id'],
                           message_data['username'],
                           message_data['first_name'],
                           message_data['last_name'],
                           message_data.get('phone_number'),
                           message_data.get('photo_id'),
                           message_data['text'],
                           message_data['date']
                       ))

        conn.commit()
        conn.close()

    def get_chat_log(self, chat_id: int) -> List[tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT m.date, u.username, u.first_name, u.last_name, m.text
                       FROM messages m
                                JOIN users u ON m.user_id = u.user_id
                       WHERE m.chat_id = ?
                       ORDER BY m.date
                       ''', (chat_id,))
        result = cursor.fetchall()
        conn.close()
        return result

    def get_user_log(self, user_id: int) -> List[tuple]:
        conn = self.get_connection()
        cursor = conn.cursor()
        cursor.execute('''
                       SELECT m.date, c.title, m.text
                       FROM messages m
                                JOIN chats c ON m.chat_id = c.chat_id
                       WHERE m.user_id = ?
                       ORDER BY m.date
                       ''', (user_id,))
        result = cursor.fetchall()
        conn.close()
        return result


# Глобальный экземпляр базы данных
db = Database()