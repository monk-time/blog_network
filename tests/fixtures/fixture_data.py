import tempfile

import pytest
from mixer.backend.django import mixer as _mixer

from posts.models import Group, Post


@pytest.fixture
def mock_media(settings):
    with tempfile.TemporaryDirectory() as temp_directory:
        settings.MEDIA_ROOT = temp_directory
        yield temp_directory


@pytest.fixture
def mixer():
    return _mixer


@pytest.fixture
def post(user):
    image = tempfile.NamedTemporaryFile(suffix='.jpg').name  # noqa: SIM115
    return Post.objects.create(
        text='Тестовый пост 1', author=user, image=image
    )


@pytest.fixture
def group():
    return Group.objects.create(
        title='Тестовая группа 1',
        slug='test-link',
        description='Тестовое описание группы',
    )


@pytest.fixture
def post_with_group(user, group):
    image = tempfile.NamedTemporaryFile(suffix='.jpg').name  # noqa: SIM115
    return Post.objects.create(
        text='Тестовый пост 2', author=user, group=group, image=image
    )


@pytest.fixture
def few_posts_with_group(mixer, user, group):
    """Return one record with the same author and group."""
    posts = mixer.cycle(20).blend(Post, author=user, group=group)
    return posts[0]


@pytest.fixture
def _another_few_posts_with_group_with_follower(
    mixer, user, another_user, group
):
    mixer.blend('posts.Follow', user=user, author=another_user)
    mixer.cycle(20).blend(Post, author=another_user, group=group)
