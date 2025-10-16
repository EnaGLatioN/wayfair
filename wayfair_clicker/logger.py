import logging
import os
from datetime import datetime


def setup_logger():
    """Настройка логгера для бота"""

    # Создаем папку для логов если нет
    if not os.path.exists('logs'):
        os.makedirs('logs')

    # Форматирование
    formatter = logging.Formatter(
        '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        datefmt='%Y-%m-%d %H:%M:%S'
    )

    # Логгер для бота
    logger = logging.getLogger('telegram_bot')
    logger.setLevel(logging.INFO)

    # Файловый обработчик
    file_handler = logging.FileHandler(
        f'logs/bot_{datetime.now().strftime("%Y%m%d")}.log',
        encoding='utf-8'
    )
    file_handler.setFormatter(formatter)

    # Консольный обработчик
    console_handler = logging.StreamHandler()
    console_handler.setFormatter(formatter)

    # Добавляем обработчики
    logger.addHandler(file_handler)
    logger.addHandler(console_handler)

    return logger