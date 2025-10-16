import subprocess
import os
import signal
import sys
import django
from django.core.management.base import BaseCommand
from logger import setup_logger
import telebot
from telebot.types import ReplyKeyboardRemove
from decouple import config

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'wayfair_clicker.wayfair_clicker.settings')
sys.path.append(os.path.dirname(os.path.abspath(__file__)))

django.setup()

from wayfair_bot.models import Token, Process, User


class Command(BaseCommand):
    help = "Telegram bot for Wayfair clicker"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.bot = telebot.TeleBot(config("TELE_TOKEN", cast=str))
        self.user_states = {}
        self.setup_handlers()
        self.logger = setup_logger()

    def setup_handlers(self):
        """Настройка обработчиков сообщений"""

        @self.bot.message_handler(commands=['start'])
        def send_welcome(message):
            """Главное меню бота"""
            user_id = message.from_user.id
            self.logger.info(f"USER ID пользователя: {user_id}")

            user, created = User.objects.get_or_create(telegram_id=user_id)

            # Создаем текстовый файл с шаблоном
            template_content = f"""# Шаблон для заполнения токена и заголовков

        token=your_token_here (Это пункт Authorization)
        X_PX_OS_VERSION=18.6.2
        Accept_Language=ru
        X_PX_VID=61dcee5d-a14b-11f0-a7ad-7b2c41dbf4aa
        Connection=keep-alive
        Accept=application/json
        X_PX_DEVICE_FP=DD6382DE-FC6A-4B59-B94E-F18334B1A71D
        wf_customer_guid=AC84D264-98B4-4816-B77A-0E846B95E5EE
        X_PX_HELLO=C1UKBwABVwEeUgoLAh4CAlUDHlIHBVIeVwQLUgUEA1VQVQZW
        wf_pageview_id=UkRVMlJrRXdOVGd0UkVNeA==
        X_PX_MOBILE_SDK_VERSION=3.2.5
        X_Graph_Type=3
        Content_Type=application/json
        X_PX_AUTHORIZATION=your_px_authorization_here
        User_Agent=WayhomeApp/20250910.12080 1.100.0 (iPhone; iOS 18.6.2; Scale/3.00)
        wf_locale=en-US
        X_PX_UUID=8f9432d2-a981-11f0-a46a-d78a670fcf5e
        AppAuthEnabled=1
        Authorization=your_bearer_token_here
        Accept_Encoding=gzip, deflate, br
        X_PX_DEVICE_MODEL=iPhone15,5
        wf_device_guid=39B9B4BC-BAC5-4DD7-8412-0637CE162DB6
        Host=www.wayfair.com
        Cookie=your_cookie_here
        X_PX_OS=iOS

        # Заполните все поля своими значениями и отправьте файл обратно
        """

            # Создаем временный файл
            with open("token_template.txt", "w", encoding="utf-8") as f:
                f.write(template_content)

            # Отправляем документ
            with open("token_template.txt", "rb") as doc:
                self.bot.send_document(
                    message.chat.id,
                    doc,
                    caption="📄 Заполните этот шаблон и отправьте обратно"
                )

            welcome_text = """
        🤖 Добро пожаловать в Wayfair Bot!

        Доступные команды:
        /del_token - Удалить не нужный токен
        /run - Запустить процесс с токеном
        /stop - Остановить активный процесс
        /status - Статус текущих процессов
        /help - Помощь по командам
        /new - Изменить токен

        📝 Отправьте заполненный файл чтобы сохранить данные
        """
            self.bot.reply_to(message, welcome_text)


        @self.bot.message_handler(content_types=['document'])
        def handle_document(message):
            """Обработка полученного документа с данными"""
            user_id = message.from_user.id

            try:
                # Получаем информацию о документе
                file_info = self.bot.get_file(message.document.file_id)
                downloaded_file = self.bot.download_file(file_info.file_path)

                # Сохраняем временный файл
                temp_filename = f"temp_{user_id}_{message.document.file_name}"
                with open(temp_filename, 'wb') as new_file:
                    new_file.write(downloaded_file)

                # Парсим файл
                token_data = parse_token_file(temp_filename)

                # Сохраняем в базу
                save_token_to_db(self, user_id, token_data)

                os.remove(temp_filename)

                self.bot.reply_to(message, "✅ Данные успешно сохранены!")

            except Exception as e:
                self.logger.error(f"Ошибка обработки документа: {e}")
                self.bot.reply_to(message, "❌ Ошибка при обработке файла")

        def parse_token_file(filename):
            """Парсит файл с токенами"""
            token_data = {}

            with open(filename, 'r', encoding='utf-8') as f:
                for line in f:
                    line = line.strip()
                    # Пропускаем пустые строки и комментарии
                    if not line or line.startswith('#'):
                        continue

                    # Разделяем ключ и значение
                    if '=' in line:
                        key, value = line.split('=', 1)
                        token_data[key.strip()] = value.strip()

            return token_data

        def save_token_to_db(self, user_id, token_data):
            """Сохраняет данные токена в базу"""
            try:
                user = User.objects.get(telegram_id=user_id)

                # Создаем или обновляем токен через связь tg_token
                if token := user.tg_token:
                    for field, value in token_data.items():
                        if hasattr(token, field):
                            setattr(token, field, value)
                    token.save()
                else:
                    # Создаем новый токен
                    token = Token.objects.create(**token_data)
                    user.tg_token = token
                    user.save()

                self.logger.info(f"Токен сохранен для user_id: {user_id}")
                return token

            except Exception as e:
                self.logger.error(f"Ошибка сохранения токена: {e}")
                raise

        @self.bot.message_handler(commands=['help'])
        def show_help(message):
            """Показать справку по командам"""
            help_text = """
                📋 Справка по командам:
                
        /del_token - Удалить не нужный токен
        /run <id_токена> - Запустить процесс с указанным токеном
        /stop - Остановить все активные процессы
        /status - Показать статус текущих процессов
        /list_tokens - Показать все доступные токены
        /new - Изменить токен
            """
            self.bot.reply_to(message, help_text)

        @self.bot.message_handler(commands=['del_token'])
        def request_token(message):
            """Запрос токена у пользователя"""

            command_parts = message.text.split("=")
            try:
                token_id = command_parts[1].strip()
                token = Token.objects.get(id=token_id)
                token.delete()
                self.bot.reply_to(message, "✅ Токен удален")
            except Token.DoesNotExist:
                self.bot.reply_to(message, "❌ Токен с указанным ID не найден")
            except Exception as e:
                self.bot.reply_to(message, f"❌ Ошибка при запуске: {e}")
            # try:
            #     user = User.objects.get(
            #         telegram_id=user_id
            #     )
            # except Exception as e:
            #     self.bot.reply_to(message, f"❌ Вы не зарегестрированный пользователь напиши /start: {e}")
            #     return
            # if user.tg_token:
            #     self.bot.reply_to(message, f"❌ У вас уже есть добавленный токен пиши  /list_tokens")
            # else:
            #     self.user_states[chat_id] = "waiting_for_token"
            #
            #     self.bot.send_message(
            #         chat_id,
            #         "Пожалуйста, введите ваш токен:",
            #         reply_markup=ReplyKeyboardRemove()
            #     )

        @self.bot.message_handler(commands=['list_tokens'])
        def list_tokens(message):
            """Показать все доступные токены"""
            try:
                tokens = Token.objects.filter()
                if tokens:
                    token_list = "📋 Доступные токены:\n\n"
                    for token in tokens:
                        token_list += f"ID: {token.id} - {token.token[:10]}...\n"
                    self.bot.reply_to(message, token_list)
                else:
                    self.bot.reply_to(message, "❌ Нет сохраненных токенов. Используйте /token чтобы добавить токен.")
            except Exception as e:
                self.bot.reply_to(message, f"❌ Ошибка при получении токенов: {e}")

        @self.bot.message_handler(commands=['new'])
        def show_status(message):
            """Показать статус процессов"""
            user_id = message.from_user.id
            command_parts = message.text.split("=")
            if len(command_parts) < 2:
                self.bot.reply_to(message,
                                  "❌ Использование: /new = токен\n")
                return
            try:
                user = User.objects.get(
                    telegram_id=user_id
                )
            except User.DoesNotExist:
                self.bot.reply_to(message, "❌ User с указанным ID не найден напишите /start")
                return
            token = Token(
                token=command_parts[1].strip()
            )
            old_t = user.tg_token
            old_t.delete()
            user.tg_token = token
            user.save()
            self.bot.reply_to(message, "✅ Новый токен сохранен!")


        @self.bot.message_handler(commands=['run'])
        def run_process(message):
            """Запуск процесса с токеном"""
            chat_id = message.chat.id
            user_id = message.from_user.id

            command_parts = message.text.split("=")

            if len(command_parts) < 2:
                self.bot.reply_to(message,
                                  "❌ Использование: /run = id_токена\n\nИспользуйте /list_tokens чтобы посмотреть доступные токены")
                return

            try:
                token_id = command_parts[1].strip()
                token = Token.objects.get(id=token_id)
                self.start_clicker_process(token, chat_id, user_id)

            except Token.DoesNotExist:
                self.bot.reply_to(message, "❌ Токен с указанным ID не найден")
            except Exception as e:
                self.bot.reply_to(message, f"❌ Ошибка при запуске: {e}")

        @self.bot.message_handler(commands=['stop'])
        def stop_process(message):
            """Остановка всех процессов"""
            user_id = message.from_user.id
            try:
                user = User.objects.get(
                    telegram_id=user_id
                )
            except User.DoesNotExist:
                self.bot.reply_to(message, "❌ User с указанным ID не найден напишите /start")
                return
            process = user.process
            if process.status:
                try:
                    os.kill(process.pid, signal.SIGTERM)
                    process.status = False
                    process.save()
                    self.bot.reply_to(message, "✅ Все процессы остановлены")
                except Exception as e:
                    process.status = False
                    process.save()
                    self.bot.reply_to(message, f"❌ Ошибка при остановке: {e}")
            else:
                self.bot.reply_to(message, "❌ Нет активных процессов для остановки")

        @self.bot.message_handler(commands=['status'])
        def show_status(message):
            """Показать статус процессов"""
            user_id = message.from_user.id
            try:
                user = User.objects.get(
                    telegram_id=user_id
                )
            except User.DoesNotExist:
                self.bot.reply_to(message, "❌ User с указанным ID не найден напишите /start")
                return
            process = user.process
            if process.status:
                status = "🟢 Процесс активен" if process.status else "🔴 Процесс завершен"
                self.bot.reply_to(message, f"📊 Статус: {status}\nPID: {process.pid}")
            else:
                self.bot.reply_to(message, "❌ Нет активных процессов")

        @self.bot.message_handler(func=lambda message: self.user_states.get(message.chat.id) == "waiting_for_token")
        def handle_token_input(message):
            """Обработка введенного токена"""
            chat_id = message.chat.id
            user_id = message.from_user.id
            token_value = message.text.strip()

            if token_value:
                # Убираем состояние ожидания
                self.user_states.pop(chat_id, None)

                try:
                    # Сохраняем токен в базу
                    token = Token.objects.create(token=token_value)
                    try:
                        user = User.objects.get(
                            telegram_id=user_id
                        )
                    except Exception as e:
                        user = None
                        self.bot.send_message(
                            chat_id,
                            "Вас нет в системе введите /start",
                            reply_markup=ReplyKeyboardRemove()
                        )
                    if user:
                        user.tg_token = token
                        user.save()

                    self.bot.send_message(
                        chat_id,
                        f"✅ Токен успешно сохранен!\nID: {token.id}\nТокен: {token_value[:10]}...",
                        reply_markup=ReplyKeyboardRemove()
                    )

                    # Показываем доступные команды
                    self.bot.send_message(
                        chat_id,
                        "Теперь вы можете:\n/list_tokens - посмотреть все токены\n/run = id - запустить процесс \n/new = новый токен - заменить токен"
                    )

                except Exception as e:
                    self.bot.reply_to(message, f"❌ Ошибка при сохранении токена: {e}")
            else:
                self.bot.reply_to(message, "❌ Токен не может быть пустым. Пожалуйста, введите токен еще раз:")

    def start_clicker_process(self, token, chat_id, user_id):
        """Запуск процесса clicker"""
        try:
            user = User.objects.get(
                telegram_id=user_id
            )
            with open("process.log", "a") as log_file:
                active_process = subprocess.Popen(
                    [
                        "poetry", "run", "python", "clicker.py",
                        "--token_id", token.id,
                        "--chat_id", str(chat_id)
                    ],
                    stdout=log_file,
                    stderr=log_file,
                    text=True,
                    bufsize=1
                )
                process = Process.objects.create(
                    pid=active_process.pid,
                )
                user.process = process
                user.save()
                self.logger.info(f"Процесс запущен. PID: {active_process.pid}")

                self.bot.send_message(
                    chat_id,
                    f"✅ Процесс запущен!\nТокен ID: {token.id}\nPID: {active_process.pid}\n\nИспользуйте /status для проверки статуса или /stop для остановки"
                )

        except Exception as e:
            self.logger.error(f"Ошибка при запуске команды: {e}")
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