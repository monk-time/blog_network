from http import HTTPStatus

from django.test import Client, TestCase

from posts.models import User


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        cls.urls_accessible_to_all = {
            '/auth/signup/': 'users/signup.html',
            '/auth/login/': 'users/login.html',
            '/auth/password_reset/': 'users/password_reset.html',
            '/auth/password_reset/done/': 'users/password_reset_done.html',
            '/auth/reset/123/123/': 'users/password_reset_confirm.html',
            '/auth/reset/done/': 'users/password_reset_complete.html',
            '/auth/logout/': 'users/logged_out.html',
        }
        cls.urls_accessible_to_authorized = {
            '/auth/password_change/': 'users/password_change.html',
            '/auth/password_change/done/': 'users/password_change_done.html',
        }

    def setUp(self):
        self.guest_client = Client()

        self.authorized_client = Client()
        self.authorized_client.force_login(UserURLTests.user)

    def test_urls_exist(self):
        """Страницы доступны любому пользователю."""
        for url in UserURLTests.urls_accessible_to_all:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_authorized(self):
        """Страницы доступны автору."""
        for url in UserURLTests.urls_accessible_to_authorized:
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Страницы перенаправят анонимного пользователя на страницу логина."""
        for url in UserURLTests.urls_accessible_to_authorized:
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_urls = {
            **UserURLTests.urls_accessible_to_authorized,
            **UserURLTests.urls_accessible_to_all,
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)
