from collections import namedtuple
from http import HTTPStatus

from django.core.cache import cache
from django.test import Client, TestCase

from ..models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        cls.user_nonauthor = User.objects.create_user(  # type: ignore
            username='test_user2'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )
        cls.post_to_delete = Post.objects.create(
            text='Тестовый пост для удаления',
            author=cls.user,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)
        self.authorized_client_nonauthor = Client()
        self.authorized_client_nonauthor.force_login(
            PostURLTests.user_nonauthor
        )

        URLData = namedtuple(
            'URL',
            ('url', 'client', 'code', 'redirect_url'),
            defaults=(self.client, HTTPStatus.OK, None),
        )
        self.urls = [
            URLData(url=''),
            URLData(url=f'/group/{self.group.slug}/'),
            URLData(url=f'/profile/{self.user.username}/'),
            URLData(url=f'/posts/{self.post.pk}/'),
            URLData(
                url='/create/',
                client=self.authorized_client,
            ),
            URLData(
                url='/create/',
                code=HTTPStatus.FOUND,
                redirect_url='/auth/login/?next=/create/',
            ),
            URLData(
                url=f'/posts/{self.post.pk}/edit/',
                client=self.authorized_client,
            ),
            URLData(
                url=f'/posts/{self.post.pk}/edit/',
                code=HTTPStatus.FOUND,
                redirect_url=f'/auth/login/?next=/posts/{self.post.pk}/edit/',
            ),
            URLData(
                url=f'/posts/{self.post.pk}/edit/',
                client=self.authorized_client_nonauthor,
                code=HTTPStatus.FOUND,
                redirect_url=f'/posts/{self.post.pk}/',
            ),
            URLData(
                url=f'/posts/{self.post_to_delete.pk}/delete/',
                client=self.authorized_client,
                code=HTTPStatus.FOUND,
                redirect_url=f'/profile/{self.user.username}/',
            ),
            URLData(
                url=f'/posts/{self.post.pk}/delete/',
                code=HTTPStatus.FOUND,
                redirect_url=(
                    f'/auth/login/?next=/posts/{self.post.pk}/delete/'
                ),
            ),
            URLData(
                url=f'/posts/{self.post.pk}/delete/',
                client=self.authorized_client_nonauthor,
                code=HTTPStatus.FOUND,
                redirect_url=f'/posts/{self.post.pk}/',
            ),
            URLData(
                url=f'/posts/{self.post.pk}/comment/',
                code=HTTPStatus.FOUND,
                redirect_url=(
                    f'/auth/login/?next=/posts/{self.post.pk}/comment/'
                ),
            ),
            URLData(
                url=f'/posts/{self.post.pk}/comment/',
                client=self.authorized_client,
                code=HTTPStatus.FOUND,
                redirect_url=f'/posts/{self.post.pk}/',
            ),
            URLData(
                url='/unexisting_page/',
                code=HTTPStatus.NOT_FOUND,
            ),
        ]

    def tearDown(self):
        cache.clear()

    def test_urls_return_correct_status_code(self):
        """Страницы возвращают корректный HTTP-код."""
        for url_data in self.urls:
            with self.subTest(url=url_data.url):
                response = url_data.client.get(url_data.url)
                self.assertEqual(response.status_code, url_data.code)

    def test_urls_redirect(self):
        """Страницы перенаправят некорректного пользователя."""
        for url_data in self.urls:
            with self.subTest(url=url_data.url):
                if not url_data.redirect_url:
                    continue
                response = url_data.client.get(url_data.url, follow=True)
                self.assertRedirects(response, url_data.redirect_url)

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_urls = {
            '': 'posts/index.html',
            f'/group/{PostURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{PostURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{PostURLTests.post.pk}/': 'posts/post_detail.html',
            f'/posts/{PostURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
