import logging
import subprocess
import os
import sys
import django
from django.core.management.base import BaseCommand

import telebot
from telebot.types import ReplyKeyboardRemove
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wayfair_clicker.wayfair_clicker.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from wayfair_bot.models import Token, Process


class Command(BaseCommand):
    help = "Telegram bot for Wayfair clicker"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = telebot.TeleBot(config("TELE_TOKEN", cast=str))
        self.user_states = {}
        self.active_processes = {}
        self.setup_handlers()

    def setup_handlers(self):
        """Настройка обработчиков сообщений"""

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            """Главное меню бота"""
            welcome_text = """
                🤖 Добро пожаловать в Wayfair Bot!
                
                Доступные команды:
                /token - Добавить новый токен
                /run - Запустить процесс с токеном
                /stop - Остановить активный процесс
                /status - Статус текущих процессов
                /help - Помощь по командам
            """
            self.bot.reply_to(message, welcome_text)

        @self.bot.message_handler(commands=['help'])
        def show_help(message):
            """Показать справку по командам"""
            help_text = """
                📋 Справка по командам:
                
                /token - Добавить новый API токен
                /run <id_токена> - Запустить процесс с указанным токеном
                /stop - Остановить все активные процессы
                /status - Показать статус текущих процессов
                /list_tokens - Показать все доступные токены
            """
            self.bot.reply_to(message, help_text)

        @self.bot.message_handler(commands=['token'])
        def request_token(message):
            """Запрос токена у пользователя"""
            chat_id = message.chat.id
            self.user_states[chat_id] = "waiting_for_token"

            self.bot.send_message(
                chat_id,
                "Пожалуйста, введите ваш токен:",
                reply_markup=ReplyKeyboardRemove()
            )

        @self.bot.message_handler(commands=['list_tokens'])
        def list_tokens(message):
            """Показать все доступные токены"""
            try:
                tokens = Token.objects.all()
                if tokens:
                    token_list = "📋 Доступные токены:\n\n"
                    for token in tokens:
                        token_list += f"ID: {token.id} - {token.token[:10]}...\n"
                    self.bot.reply_to(message, token_list)
                else:
                    self.bot.reply_to(message, "❌ Нет сохраненных токенов. Используйте /token чтобы добавить токен.")
            except Exception as e:
                self.bot.reply_to(message, f"❌ Ошибка при получении токенов: {e}")

        @self.bot.message_handler(commands=['run'])
        def run_process(message):
            """Запуск процесса с токеном"""
            chat_id = message.chat.id
            command_parts = message.text.split()
            if len(command_parts) < 2:
                self.bot.reply_to(message,
                                  "❌ Использование: /run <id_токена>\n\nИспользуйте /list_tokens чтобы посмотреть доступные токены")
                return

            try:
                token_id = int(command_parts[1])
                token = Token.objects.get(id=token_id)
                self.start_clicker_process(chat_id, token)

            except Token.DoesNotExist:
                self.bot.reply_to(message, "❌ Токен с указанным ID не найден")
            except ValueError:
                self.bot.reply_to(message, "❌ Неверный формат ID. ID должен быть числом")
            except Exception as e:
                self.bot.reply_to(message, f"❌ Ошибка при запуске: {e}")

        @self.bot.message_handler(commands=['stop'])
        def stop_process(message):
            """Остановка всех процессов"""
            chat_id = message.chat.id

            if chat_id in self.active_processes:
                try:
                    self.active_processes[chat_id].terminate()
                    del self.active_processes[chat_id]
                    self.bot.reply_to(message, "✅ Все процессы остановлены")
                except Exception as e:
                    self.bot.reply_to(message, f"❌ Ошибка при остановке: {e}")
            else:
                self.bot.reply_to(message, "❌ Нет активных процессов для остановки")

        @self.bot.message_handler(commands=['status'])
        def show_status(message):
            """Показать статус процессов"""
            chat_id = message.chat.id

            if chat_id in self.active_processes:
                process = self.active_processes[chat_id]
                status = "🟢 Процесс активен" if process.poll() is None else "🔴 Процесс завершен"
                self.bot.reply_to(message, f"📊 Статус: {status}\nPID: {process.pid}")
            else:
                self.bot.reply_to(message, "❌ Нет активных процессов")

        @self.bot.message_handler(func=lambda message: self.user_states.get(message.chat.id) == "waiting_for_token")
        def handle_token_input(message):
            """Обработка введенного токена"""
            chat_id = message.chat.id
            token_value = message.text.strip()

            if token_value:
                # Убираем состояние ожидания
                self.user_states.pop(chat_id, None)

                try:
                    # Сохраняем токен в базу
                    token = Token.objects.create(token=token_value)

                    self.bot.send_message(
                        chat_id,
                        f"✅ Токен успешно сохранен!\nID: {token.id}\nТокен: {token_value[:10]}...",
                        reply_markup=ReplyKeyboardRemove()
                    )

                    # Показываем доступные команды
                    self.bot.send_message(
                        chat_id,
                        "Теперь вы можете:\n/list_tokens - посмотреть все токены\n/run <id> - запустить процесс"
                    )

                except Exception as e:
                    self.bot.reply_to(message, f"❌ Ошибка при сохранении токена: {e}")
            else:
                self.bot.reply_to(message, "❌ Токен не может быть пустым. Пожалуйста, введите токен еще раз:")

    def start_clicker_process(self, chat_id, token):
        """Запуск процесса clicker"""
        try:
            with open("process.log", "a") as log_file:
                active_process = subprocess.Popen(
                    [
                        "poetry", "run", "python", "bot_click.py",
                        "--token", token.token,
                    ],
                    stdout=log_file,
                    stderr=log_file,
                    text=True
                )

                self.active_processes[chat_id] = active_process
                Process.objects.create(
                    pid=active_process.pid,
                    pc_token=token
                )
                logging.info(f"Процесс запущен. PID: {active_process.pid}")

                self.bot.send_message(
                    chat_id,
                    f"✅ Процесс запущен!\nТокен ID: {token.id}\nPID: {active_process.pid}\n\nИспользуйте /status для проверки статуса или /stop для остановки"
                )

        except Exception as e:
            logging.error(f"Ошибка при запуске команды: {e}")
            self.bot.send_message(chat_id, f"❌ Ошибка при запуске процесса: {e}")

    def handle(self, *args, **options):
        """Основной метод запуска бота"""
        self.stdout.write("Бот запущен...")
        self.start_bot()

    def start_bot(self):
        """Запуск polling бота"""
        while True:
            try:
                self.bot.polling(none_stop=True)
            except Exception as e:
                self.stderr.write(f"Ошибка: {e}")
                continue