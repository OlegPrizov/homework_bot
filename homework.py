import logging
import os
import time

from dotenv import load_dotenv
from http import HTTPStatus
import requests
import telegram

import Exceptions

load_dotenv()

PRACTICUM_TOKEN = os.getenv('PRACTICUM_TOKEN')
TELEGRAM_TOKEN = os.getenv('TELEGRAM_TOKEN')
TELEGRAM_CHAT_ID = os.getenv('TELEGRAM_CHAT_ID')

RETRY_PERIOD = 600
ENDPOINT = 'https://practicum.yandex.ru/api/user_api/homework_statuses/'
HEADERS = {'Authorization': f'OAuth {PRACTICUM_TOKEN}'}

logging.basicConfig(
    level=logging.DEBUG,
    filename='program.log',
    format='%(asctime)s, %(levelname)s, %(message)s, %(name)s'
)

HOMEWORK_VERDICTS = {
    'approved': 'Работа проверена: ревьюеру всё понравилось. Ура!',
    'reviewing': 'Работа взята на проверку ревьюером.',
    'rejected': 'Работа проверена: у ревьюера есть замечания.'
}


def check_tokens():
    """Проверяет доступность переменных окружения."""
    indicator = True
    tokens = (
        ('PRACTICUM_TOKEN', PRACTICUM_TOKEN),
        ('TELEGRAM_TOKEN', TELEGRAM_TOKEN),
        ('TELEGRAM_CHAT_ID', TELEGRAM_CHAT_ID)
    )
    for name, token in tokens:
        if not token:
            logging.critical(f'Нет {name}')
            indicator = False
    return indicator


def send_message(bot, message):
    """Отправка сообщения в Telegram чат."""
    try:
        logging.debug(f'Отправляем сообщение {message}')
        bot.send_message(chat_id=TELEGRAM_CHAT_ID, text=message)
    except telegram.error.TelegramError as error:
        logging.error(f'Ошибка отправки {error}')
        return False
    else:
        logging.debug(f'Отправлено сообщение {message}')
        return True


def get_api_answer(timestamp):
    """Делает запрос к эндпоинту API-сервиса."""
    parameters = {
        'url': ENDPOINT,
        'headers': HEADERS,
        'params': {'from_date': timestamp},
    }
    logging.debug('Запрос к {url} с {params}'.format(**parameters))
    try:
        response = requests.get(**parameters)
        if response.status_code != HTTPStatus.OK:
            raise Exceptions.IncorrectStatusCode(
                f'Неверный код ответа:{response.status_code}, '
                f'{response.reason}, {response.text}.')
        return response.json()
    except Exception as error:
        raise ConnectionError(
            'Ошибка {error} при запросе к {url} c параметрами {params}'.format
            (
                error,
                **parameters
            )
        )


def check_response(response):
    """Проверяет ответ на соответствие документации."""
    logging.debug(f'Начало проверки {response}')
    if not isinstance(response, dict):
        raise TypeError('Неверный тип данных')
    homeworks = response.get('homeworks')
    if homeworks is None:
        raise Exceptions.EmptyAnswerFromApi('В ответе нет homeworks')
    homeworks = response.get('homeworks')
    if not isinstance(homeworks, list):
        raise TypeError('Неверный тип данных')
    return homeworks


def parse_status(homework):
    """Статус проверки конкретной домашней работы."""
    if 'homework_name' not in homework:
        raise KeyError('Невожможно обработать запрос')
    homework_status = homework.get('status')
    if homework_status not in HOMEWORK_VERDICTS:
        raise ValueError('Дз c неожиданным статусом')
    homework_name = homework.get('homework_name')
    verdict = HOMEWORK_VERDICTS[homework_status]
    return f'Изменился статус проверки работы "{homework_name}". {verdict}'


def main():
    """Основная логика работы бота."""
    if not check_tokens():
        logging.critical('Нет нужных переменных окружения')
        raise Exceptions.NoRequiredVariables('Нет нужных переменных окружения')
    current_report = {
        'name': '',
        'message': ''
    }
    prev_report = {
        'name': '',
        'message': ''
    }
    bot = telegram.Bot(token=TELEGRAM_TOKEN)
    timestamp = 0
    while True:
        try:
            response = get_api_answer(timestamp)
            homeworks = check_response(response)
            if homeworks:
                needed_homework = homeworks[0]
                homework = parse_status(needed_homework)
                current_report['message'] = homework
                current_report['name'] = needed_homework.get('homework_name')
            else:
                current_report['message'] = 'Нет новых статусов'
            if current_report != prev_report:
                if send_message(bot, current_report['message']):
                    prev_report = current_report.copy()
                    timestamp = response.get('current_date', timestamp)
                else:
                    logging.debug('Нет новых статусов')
        except Exceptions.EmptyAnswerFromApi as error:
            logging.error(f'Ошибка: {error}', exc_info=True)
        except Exception as error:
            message = f'Сбой в работе программы: {error}'
            logging.debug(message)
            current_report['message'] = message
            if current_report != prev_report:
                send_message(bot, current_report['message'])
                prev_report = current_report.copy()
        finally:
            time.sleep(RETRY_PERIOD)


if __name__ == '__main__':
    main()
