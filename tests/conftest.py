from pathlib import Path

import pytest

BASE_DIR = Path(__file__).resolve().parent.parent
PROJECT_DIR_NAME = 'app'
MANAGE_PATH = BASE_DIR / PROJECT_DIR_NAME
# проверяем, что в корне репозитория лежит папка с проектом
if not MANAGE_PATH.exists() or not MANAGE_PATH.is_dir():
    pytest.fail(
        f'В директории `{BASE_DIR}` не найдена папка c проектом `{PROJECT_DIR_NAME}`. '
        f'Убедитесь, что у вас верная структура проекта.'
    )

FILENAME = 'manage.py'
# проверяем, что структура проекта верная, и manage.py на месте
if not (MANAGE_PATH / FILENAME).is_file():
    pytest.fail(
        f'В директории `{MANAGE_PATH}` не найден файл `{FILENAME}`. '
        f'Убедитесь, что у вас верная структура проекта.'
    )

from yatube.settings import INSTALLED_APPS  # noqa: E402

assert any(
    app in INSTALLED_APPS for app in ['posts.apps.PostsConfig', 'posts']
), 'Пожалуйста зарегистрируйте приложение в `settings.INSTALLED_APPS`'

pytest_plugins = [
    'tests.fixtures.fixture_user',
    'tests.fixtures.fixture_data',
]
