import logging
import subprocess
import os
import signal
import time

import telebot
from telebot.types import ReplyKeyboardRemove, CallbackQuery
from decouple import config


# TELE_TOCKEN = "8407176850:AAF3qq3LQl2WR_cjOHmodOh9pKVvd2uFU_g"

bot = telebot.TeleBot(config("TELE_TOKEN", cast=str))


@bot.message_handler(commands=['start',])
def send_welcome(message):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            "Да",
            callback_data="start-bot"
        ),
        telebot.types.InlineKeyboardButton(
            "Нет",
            callback_data="goodbay"
        ),
        telebot.types.InlineKeyboardButton(
            "Завершить процесс?",
            callback_data="finish-parse"
        ),
    )
    bot.reply_to(message, "Запустить бота?", reply_markup=keyboard)


@bot.callback_query_handler(func=lambda call: call.data == "start-bot")
def start_bot(call: CallbackQuery):
    chat_id = call.message.chat.id
    print(f"Chat111111111111 ID: {chat_id}")
    keyboard = telebot.types.InlineKeyboardMarkup()
    for i in rates.values():
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                i,
                callback_data=f"take-rates-{i}"
            ),
        )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Выберите курс",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data.startswith("proc-start"))
def start_bot(call: CallbackQuery):
    processes = int(call.data.replace("proc-start-", ""))
    keyboard = telebot.types.InlineKeyboardMarkup()
    record = {}
    records_to_insert = []
    try:
        if len(get_active_records(create_connection())) == 1:
            record = get_active_records(create_connection())[0]
        else:
            logging.error("В базе больше одной активной записи.")
        with open("bot.log", "a") as log_file:
            for i in range(min(len(proxies), processes)):
                time.sleep(0.100)
                active_process = subprocess.Popen(
                    ["poetry", "run", "python", "bot_click.py",
                     "--rate", str(record.get("disperce")),
                     "--min_summ", str(record.get("min_summ")),
                     "--processes", str(processes),
                     "--proxy", str(proxies[i]),
                     "--email", str(AUTHS[i].get("email", None)),
                     "--password", str(AUTHS[i].get("password", None)),
                     ],
                    stdout=log_file,
                    stderr=log_file,
                    text=True
                )
                records_to_insert.append((
                    f"poetry run python bot_click.py "
                    f"--rate {str(record.get('disperce'))} "
                    f"--min_summ {str(record.get('min_summ'))} "
                    f"--processes {str(processes)} "
                    f"--email {str(record.get('email'))}"
                    f"--password {str(record.get('password'))}",
                    active_process.pid
                ))
                logging.info(f"Процесс запущен.---- {active_process.pid}")
        insert_process(create_connection(), records_to_insert)
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                "Остановить",
                callback_data=f"finish-parse"
            ),
        )
    except Exception as e:
        logging.error(f"Ошибка при запуске команды: {e}")

    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Бот запущен",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "finish-parse")
def start_bot(call: CallbackQuery):
    keyboard = telebot.types.InlineKeyboardMarkup()
    keyboard.row(
        telebot.types.InlineKeyboardButton(
            "Да",
            callback_data="start-bot"
        ),
        telebot.types.InlineKeyboardButton(
            "Нет",
            callback_data="goodbay"
        ),
    )
    for process in get_active_processes(create_connection()):
        try:
            pid = process.get("pid")
            os.kill(pid, signal.SIGTERM)
            logging.info(f"Процесс с PID {pid} успешно завершен.")
        except OSError as e:
            logging.info(f"Ошибка при попытке завершения процесса с PID {pid}: {e}")
    update_processes(create_connection())

    update_positions(
        connection=create_connection(),
        status=False,
    )
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="Бот остановлен\nЗапустить заново?",
        reply_markup=keyboard
    )


@bot.callback_query_handler(func=lambda call: call.data == "goodbay")
def start_bot(call: CallbackQuery):
    bot.edit_message_text(
        chat_id=call.message.chat.id,
        message_id=call.message.message_id,
        text="До скорых встреч!",
    )


@bot.message_handler(content_types=['text'])
def take_min_amount(message):
    summa = int(message.json.get("text")) if message.json.get("text").isdigit() else None
    if summa is None:
        bot.send_message(
            chat_id=message.from_user.id,
            text=f"Неверный формат данных, попробуй ещё раз",
            reply_markup=ReplyKeyboardRemove()
        )
    if (summa >= 1000) and (summa is not None):
        update_positions(
            connection=create_connection(),
            min_summ=int(message.json.get("text")),
        )
        curse = get_active_records(connection=create_connection())[0].get("rate", None)
        keyboard = telebot.types.InlineKeyboardMarkup()
        keyboard.row(
            telebot.types.InlineKeyboardButton(
                "-",
                callback_data=f"dispersion-minus-{0.1}"
            ),
            telebot.types.InlineKeyboardButton(
                "+",
                callback_data=f"dispersion-plus-{0.1}"
            ),
        ).row(
            telebot.types.InlineKeyboardButton(
                "Готово",
                callback_data=f"dispersion-ready-{0.1}"
            ),
        )
        bot.send_message(
            chat_id=message.from_user.id,
            text=f"Отклонение от курса: {0.1}% (max: {curse + (curse * 0.1 / 100)})",
            reply_markup=keyboard
        )
        return


while True:
    try:
        bot.polling(none_stop=True)
    except:
        continue
