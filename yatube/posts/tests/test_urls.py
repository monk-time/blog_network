from http import HTTPStatus

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
        cls.urls_accessible_to_all = {
            '': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.user.username}/': 'posts/profile.html',
            f'/posts/{cls.post.pk}/': 'posts/post_detail.html',
        }
        cls.urls_accessible_to_author = {
            f'/posts/{cls.post.pk}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(PostURLTests.user)

        self.authorized_client_nonauthor = Client()
        self.authorized_client_nonauthor.force_login(
            PostURLTests.user_nonauthor
        )

    def test_urls_exist(self):
        """Страницы доступны любому пользователю."""
        for url in PostURLTests.urls_accessible_to_all:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_author(self):
        """Страницы доступны автору."""
        for url in PostURLTests.urls_accessible_to_author:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Страницы перенаправят анонимного пользователя на страницу логина."""
        for url in PostURLTests.urls_accessible_to_author:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_post_edit_url_redirects_nonauthor(self):
        """Страница /posts/<post_id>/edit/ перенаправит пользователя,
        не являющегося автором, на страницу поста.
        """
        response = self.authorized_client_nonauthor.get(
            f'/posts/{PostURLTests.post.pk}/edit/', follow=True
        )
        self.assertRedirects(response, f'/posts/{PostURLTests.post.pk}/')

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls = {
            **PostURLTests.urls_accessible_to_all,
            **PostURLTests.urls_accessible_to_author,
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def test_unexisting_url_doesnt_exist(self):
        """Несуществующая страница не существует."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)
