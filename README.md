# homework_bot

## Бот для оповещения об этапах проектов, их статусов и внесении изменений.

### Этот бот выполняет следующие функции:
1. Раз в 10 минут обращается к API сервиса Практикум.Домашка и проверяет статус отправленной на ревью домашней работы;
2. При обновлении статуса анализирует ответ API и отправляет студенту соответствующее уведомление в Telegram;
3. Логирует свою работу и сообщает о важных проблемах сообщением в Telegram.

### Стек
- Python 3.10.5
- python-telegram-bot 13.7

### Как запустить проект:

Клонировать репозиторий и перейти в него в командной строке:
```
git clone git@github.com:OlegPrizov/homework_bot.git
cd homework_bot
```

Cоздать и активировать виртуальное окружение:
```
python3 -m venv env
source env/bin/activate
python3 -m pip install --upgrade pip
```

Установить зависимости из файла requirements.txt:
```
pip install -r requirements.txt
```

Создать и заполнить файл .env:

Запустить проект:
```
pethon homework.py
```

### Автор 

[Олег Призов](https://github.com/OlegPrizov) 
dockerhub_username: olegprizov
