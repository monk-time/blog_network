import re

import pytest
from django.contrib.auth import get_user_model
from django.db.models import fields

try:
    from posts.models import Comment
except ImportError:
    pytest.fail('Не найдена модель Comment')

try:
    from posts.models import Post
except ImportError:
    pytest.fail('Не найдена модель Post')


def search_field(fields, attname):
    for field in fields:
        if attname == field.attname:
            return field
    return None


def search_refind(execution, user_code):
    """Поиск запуска."""
    return any(
        re.search(execution, temp_line) for temp_line in user_code.split('\n')
    )


class TestComment:
    def test_comment_model(self):
        model_fields = Comment._meta.fields
        text_field = search_field(model_fields, 'text')
        assert text_field is not None, (
            'Добавьте название события `text` модели `Comment`'
        )
        assert isinstance(text_field, fields.TextField), (
            'Свойство `text` модели `Comment` должно быть текстовым `TextField`'
        )

        pub_date_field_name = 'created'
        pub_date_field = search_field(model_fields, 'pub_date')
        if pub_date_field is not None:
            pub_date_field_name = 'pub_date'
        else:
            pub_date_field = search_field(model_fields, 'created')
            if pub_date_field is not None:
                pub_date_field_name = 'created'

        assert pub_date_field is not None, (
            'Добавьте дату и время проведения события '
            f'`{pub_date_field_name}` модели `Comment`'
        )
        assert isinstance(pub_date_field, fields.DateTimeField), (
            f'Свойство `{pub_date_field_name}` модели `Comment` '
            'должно быть датой и время `DateTimeField`'
        )
        assert pub_date_field.auto_now_add, (
            f'Свойство `{pub_date_field_name}` модели `Comment` '
            'должно быть `auto_now_add`'
        )

        author_field = search_field(model_fields, 'author_id')
        assert author_field is not None, (
            'Добавьте пользователя, автор который создал '
            'событие `author` модели `Comment`'
        )
        assert isinstance(author_field, fields.related.ForeignKey), (
            'Свойство `author` модели `Comment` '
            'должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert author_field.related_model == get_user_model(), (
            'Свойство `author` модели `Comment` '
            'должно быть ссылкой на модель пользователя `User`'
        )

        post_field = search_field(model_fields, 'post_id')
        assert post_field is not None, (
            'Добавьте свойство `group` в модель `Comment`'
        )
        assert isinstance(post_field, fields.related.ForeignKey), (
            'Свойство `group` модели `Comment` '
            'должно быть ссылкой на другую модель `ForeignKey`'
        )
        assert post_field.related_model == Post, (
            'Свойство `group` модели `Comment` '
            'должно быть ссылкой на модель `Post`'
        )

    @pytest.mark.django_db(transaction=True)
    def test_comment_add_view(self, client, post):
        try:
            response = client.get(f'/posts/{post.id}/comment')
        except Exception as e:
            pytest.fail(
                f'Страница `/posts/<post_id>/comment/` работает неправильно. Ошибка: `{e}`'
            )
        if (
            response.status_code in {301, 302}
            and response.url == f'/posts/{post.id}/comment/'
        ):
            url = f'/posts/{post.id}/comment/'
        else:
            url = f'/posts/{post.id}/comment'
        assert response.status_code != 404, (
            'Страница `/posts/<post_id>/comment/` не найдена, проверьте этот адрес в *urls.py*'
        )

        response = client.post(url, data={'text': 'Новый коммент!'})
        if not (
            response.status_code in {301, 302}
            and response.url.startswith('/auth/login')
        ):
            pytest.fail(
                'Проверьте, что не авторизованного пользователя '
                '`/posts/<post_id>/comment/` отправляете на страницу авторизации'
            )

    @pytest.mark.django_db(transaction=True)
    def test_comment_add_auth_view(self, user_client, post):
        try:
            response = user_client.get(f'/posts/{post.id}/comment')
        except Exception as e:
            pytest.fail(
                f'Страница `/posts/<post_id>/comment/` работает неправильно. Ошибка: `{e}`'
            )
        if (
            response.status_code in {301, 302}
            and response.url == f'/posts/{post.id}/comment/'
        ):
            url = f'/posts/{post.id}/comment/'
        else:
            url = f'/posts/{post.id}/comment'
        assert response.status_code != 404, (
            'Страница `/posts/<post_id>/comment/` не найдена, проверьте этот адрес в *urls.py*'
        )

        text = 'Новый коммент 94938!'
        response = user_client.post(url, data={'text': text})

        assert response.status_code in {301, 302}, (
            'Проверьте, что со страницы `/posts/<post_id>/comment/` '
            'после создания комментария перенаправляете на страницу поста'
        )
        comment = Comment.objects.filter(
            text=text, post=post, author=post.author
        ).first()
        assert comment is not None, (
            'Проверьте, что вы создаёте новый комментарий `/posts/<post_id>/comment/`'
        )
        assert response.url.startswith(f'/posts/{post.id}'), (
            'Проверьте, что перенаправляете на страницу поста '
            '`/posts/<post_id>/` после добавления нового комментария'
        )
