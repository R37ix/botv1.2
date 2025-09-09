import logging
import re
from datetime import datetime, time
from typing import Optional, List, Dict, Any

from telegram import Update, constants
from telegram.ext import (
    Application, CommandHandler, MessageHandler, ContextTypes,
    filters, CallbackContext
)
from telegram.error import BadRequest

from database import db
import config

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)


class ClassBot:
    def __init__(self):
        self.application = None

    async def is_admin(self, update: Update, context: ContextTypes.DEFAULT_TYPE) -> bool:
        """Проверяет, является ли пользователь администратором"""
        if update.effective_chat.type == 'private':
            return update.effective_user.id in config.ADMIN_IDS

        try:
            member = await update.effective_chat.get_member(update.effective_user.id)
            return member.status in ['administrator', 'creator']
        except Exception as e:
            logger.error(f"Ошибка при проверке прав: {e}")
            return False

    # Basic commands
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /start"""
        welcome_text = (
            "👋 Привет! Я бот этого класса.\n\n"
            "📚 Доступные команды:\n"
            "/start - начать работу\n"
            "/help - помощь\n"
            "/get_hw - получить домашнее задание\n"
            "/get_ready_hw - получить готовое домашнее задание\n"
            "/duty - узнать дежурных\n"
            "/schedule - получить расписание\n\n"
        )
        await update.message.reply_text(welcome_text)

    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик команды /help"""
        help_text = (
            "📖 Помощь по командам бота v1.2:\n\n"
            "Для всех:\n"
            "/get_hw - получить домашнее задание\n"
            "/get_ready_hw - получить готовое домашнее задание\n"
            "/duty - узнать дежурных\n"
            "/schedule - получить расписание\n\n"
            "Для админов:\n"
            "/post_hw [текст] - установить ДЗ\n"
            "/post_ready_hw [текст] - установить готовое ДЗ\n"
            "/set_duty @user1 @user2 - установить дежурных\n"
            "/post_schedule [текст] - установить расписание\n"
            "/get_chat_log - получить лог чата\n"
            "https://nash10Aklacc.ru/ - наш сайт, список изменений бота\n"
            "/get_user_log @user - получить лог пользователя\n\n"
        )
        await update.message.reply_text(help_text)

    # Homework functions
    async def post_hw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка домашнего задания"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажите текст домашнего задания!")
            return

        homework_text = ' '.join(context.args)
        chat_id = update.effective_chat.id

        db.save_homework(chat_id, homework_text)
        await update.message.reply_text("✅ Домашнее задание сохранено!")

    async def get_hw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение домашнего задания"""
        chat_id = update.effective_chat.id
        homework = db.get_homework(chat_id)

        if homework:
            await update.message.reply_text(f"📚 Домашнее задание:\n\n{homework}")
        else:
            await update.message.reply_text("📚 Домашнее задание не задано.")


# ---------------------------------------------------------------------------------------------
    async def post_ready_hw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка домашнего задания"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажите текст готового домашнего задания!")
            return

        ready_homework_text = ' '.join(context.args)
        chat_id = update.effective_chat.id

        db.save_homework(chat_id, ready_homework_text)
        await update.message.reply_text("✅ Готовое домашнее задание сохранено!")

    async def get_ready_hw(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение домашнего задания"""
        chat_id = update.effective_chat.id
        ready_homework = db.get_ready_homework(chat_id)

        if ready_homework:
            await update.message.reply_text(f"📚 Домашнее задание:\n\n{ready_homework}")
        else:
            await update.message.reply_text("📚 Домашнего задания нет.")

    # Duty functions
    async def set_duty(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка дежурных"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        if len(context.args) < 2:
            await update.message.reply_text("❌ Укажите двух пользователей через @username!")
            return

        user1 = context.args[0].lstrip('@')
        user2 = context.args[1].lstrip('@')

        db.save_duty(update.effective_chat.id, 0, user1, 0, user2)
        await update.message.reply_text(f"✅ Дежурные установлены: @{user1} и @{user2}")

    async def duty(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Показ дежурных"""
        duty = db.get_duty(update.effective_chat.id)

        if duty:
            user1, user2 = duty
            await update.message.reply_text(f"👥 Дежурные на сегодня: @{user1} и @{user2}")
        else:
            await update.message.reply_text("👥 Дежурные не назначены.")

    # Schedule functions
    async def post_schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Установка расписания"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажите текст расписания!")
            return

        schedule_text = ' '.join(context.args)
        chat_id = update.effective_chat.id

        db.save_schedule(chat_id, schedule_text)
        await update.message.reply_text("✅ Расписание сохранено!")

    async def schedule(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение расписания"""
        chat_id = update.effective_chat.id
        schedule = db.get_schedule(chat_id)

        if schedule:
            await update.message.reply_text(f"📅 Расписание:\n\n{schedule}")
        else:
            await update.message.reply_text("📅 Расписание не установлено.")

    # Reminder functions
  #  async def remind(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
      #  """Установка напоминания"""
      #  if not await self.is_admin(update, context):
        #    await update.message.reply_text("❌ Эта команда только для администраторов!")
        #    return

      #  if len(context.args) < 2:
       #     await update.message.reply_text("❌ Формат: /remind HH:MM текст напоминания")
       #     return

      #  time_pattern = r'(\d{1,2}):(\d{2})'
      #  match = re.match(time_pattern, context.args[0])

      #  if not match:
      #      await update.message.reply_text("❌ Неверный формат времени. Используйте HH:MM")
      #      return

      #  hours, minutes = map(int, match.groups())
       # reminder_text = ' '.join(context.args[1:])

     #   job_id = f"reminder_{update.effective_chat.id}_{datetime.now().timestamp()}"

     #   db.save_reminder(update.effective_chat.id, reminder_text, f"{hours:02d}:{minutes:02d}", job_id)

      #  context.job_queue.run_daily(
      #      self.send_reminder,
      #      time=time(hour=hours, minute=minutes),
   #         data=job_id,
       #     name=job_id
       # )

     #   await update.message.reply_text(f"✅ Напоминание установлено на {hours:02d}:{minutes:02d}")

  #  async def send_reminder(self, context: CallbackContext):
  #      """Отправка напоминания"""
   #     job_id = context.job.data
   #     reminder_data = db.get_reminder(job_id)

   #     if reminder_data:
    #        chat_id, message = reminder_data
    #        await context.bot.send_message(chat_id, f"⏰ Напоминание: {message}")

    # Archive functions
    async def archive_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Архивация сообщения"""
        try:
            message = update.effective_message
            user = update.effective_user
            chat = update.effective_chat

            message_data = {
                'message_id': message.message_id,
                'chat_id': chat.id,
                'chat_type': chat.type,
                'chat_title': chat.title if hasattr(chat, 'title') else None,
                'chat_username': chat.username if hasattr(chat, 'username') else None,
                'user_id': user.id,
                'username': user.username,
                'first_name': user.first_name,
                'last_name': user.last_name,
                'phone_number': None,
                'photo_id': None,
                'text': message.text or message.caption or '',
                'date': message.date
            }

            db.save_message(message_data)

        except Exception as e:
            logger.error(f"Ошибка при архивации сообщения: {e}")

    async def get_chat_log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение лога чата"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        chat_id = update.effective_chat.id
        messages = db.get_chat_log(chat_id)

        if not messages:
            await update.message.reply_text("📝 Нет сообщений в архиве для этого чата.")
            return

        log_text = f"Лог чата {chat_id}\n{'=' * 50}\n\n"
        for msg_date, username, first_name, last_name, text in messages:
            name = f"@{username}" if username else f"{first_name} {last_name}".strip()
            log_text += f"[{msg_date}] {name}: {text}\n"

        try:
            await context.bot.send_document(
                chat_id=update.effective_user.id,
                document=log_text.encode('utf-8'),
                filename=f"chat_log_{chat_id}.txt"
            )
            await update.message.reply_text("📁 Лог чата отправлен в ваши личные сообщения.")
        except BadRequest:
            await update.message.reply_text("❌ Напишите мне в личные сообщения сначала!")

    async def get_user_log(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Получение лога пользователя"""
        if not await self.is_admin(update, context):
            await update.message.reply_text("❌ Эта команда только для администраторов!")
            return

        if not context.args:
            await update.message.reply_text("❌ Укажите username пользователя!")
            return

        username = context.args[0].lstrip('@')
        user_id = 123456789

        messages = db.get_user_log(user_id)

        if not messages:
            await update.message.reply_text("📝 Нет сообщений в архиве для этого пользователя.")
            return

        log_text = f"Лог пользователя @{username}\n{'=' * 50}\n\n"
        for msg_date, chat_title, text in messages:
            log_text += f"[{msg_date}] {chat_title}: {text}\n"

        try:
            await context.bot.send_document(
                chat_id=update.effective_user.id,
                document=log_text.encode('utf-8'),
                filename=f"user_log_{username}.txt"
            )
            await update.message.reply_text("📁 Лог пользователя отправлен в ваши личные сообщения.")
        except BadRequest:
            await update.message.reply_text("❌ Напишите мне в личные сообщения сначала!")

    # Utility functions
    async def error_handler(self, update: object, context: ContextTypes.DEFAULT_TYPE):
        """Обработчик ошибок"""
        logger.error(msg="Exception while handling an update:", exc_info=context.error)

    def setup_handlers(self):
        """Настройка обработчиков"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help_command))
        self.application.add_handler(CommandHandler("post_hw", self.post_hw))
        self.application.add_handler(CommandHandler("get_hw", self.get_hw))
        self.application.add_handler(CommandHandler("set_duty", self.set_duty))
        self.application.add_handler(CommandHandler("duty", self.duty))
        self.application.add_handler(CommandHandler("post_schedule", self.post_schedule))
        self.application.add_handler(CommandHandler("schedule", self.schedule))
        self.application.add_handler(CommandHandler("get_chat_log", self.get_chat_log))
        self.application.add_handler(CommandHandler("get_user_log", self.get_user_log))
        self.application.add_handler(MessageHandler(filters.ALL & ~filters.COMMAND, self.archive_message))
        self.application.add_error_handler(self.error_handler)

    def run(self):
        """Запуск бота"""
        self.application = Application.builder().token(config.BOT_TOKEN).build()
        self.setup_handlers()
        db.clear_old_duty()
        logger.info("Бот запущен...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    bot = ClassBot()
    bot.run()


if __name__ == "__main__":
    main()