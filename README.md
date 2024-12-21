# blog_network
### Описание
Сервис социальной сети блогеров. Реализован фронтенд через шаблонизатор Django на MVT-архитектуре. Поддерживается регистрация и управление пользователями, сообщества, комментирование, редактирование записей, загрузка картинок и подписка на авторов.

Также см. два варианта REST API для этого проекта: [на DRF](https://github.com/monk-time/blog_network_api) и [на FastAPI](https://github.com/monk-time/blog_network_fastapi).

### Технологии
- Python 3.13
- Django 5.1
- SQLite 3
- uv

### Запуск проекта в dev-режиме
1. Подготовьте виртуальное окружение:
    ```bash
    uv sync
    ```
2. Выполните миграции и запустите проект:
    ```bash
    cd app
    uv run manage.py migrate
    uv run manage.py runserver
    ```
3. Для запуска тестов:
    ```bash
    uv run manage.py test
    ```

### Автор
Дмитрий Богорад [@monk-time](https://github.com/monk-time)
