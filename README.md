# blog_network
### Описание
Сервис социальной сети блогеров. Реализован фронтенд через шаблонизатор Django на MVT-архитектуре. Поддерживается регистрация и управление пользователями, сообщества, комментирование, редактирование записей, загрузка картинок и подписка на авторов.

Также см. два варианта REST API для этого проекта: [на DRF](https://github.com/monk-time/blog_network_api) и [на FastAPI](https://github.com/monk-time/blog_network_fastapi).

### Технологии
- Python 3.7
- Django 2.2.19
- SQLite 3
### Запуск проекта в dev-режиме
1. Cоздайте и активируйте виртуальное окружение:
    ```bash
    python3 -m venv venv
    # Для Linux/macOS:
    source venv/bin/activate
    # Для Windows:
    source venv/Scripts/activate
    ```
2. Установите зависимости из файла requirements.txt:
    ```bash
    python3 -m pip install --upgrade pip
    pip install -r requirements.txt
    ```
3. Выполните миграции и запустите проект:
    ```bash
    python3 manage.py migrate
    python3 manage.py runserver
    ```
### Автор
Дмитрий Богорад [@monk-time](https://github.com/monk-time)
