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
        cls.urls_accessible_to_all = (
            ('/auth/signup/', 'users/signup.html', 'GET'),
            ('/auth/login/', 'users/login.html', 'GET'),
            ('/auth/password_reset/', 'users/password_reset.html', 'GET'),
            (
                '/auth/password_reset/done/',
                'users/password_reset_done.html',
                'GET',
            ),
            (
                '/auth/reset/123/123/',
                'users/password_reset_confirm.html',
                'GET',
            ),
            ('/auth/reset/done/', 'users/password_reset_complete.html', 'GET'),
            ('/auth/logout/', 'users/logged_out.html', 'POST'),
        )
        cls.urls_accessible_to_authorized = (
            ('/auth/password_change/', 'users/password_change.html', 'GET'),
            (
                '/auth/password_change/done/',
                'users/password_change_done.html',
                'GET',
            ),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UserURLTests.user)

    def test_urls_exist(self):
        """Страницы доступны любому пользователю."""
        for url, _, method in UserURLTests.urls_accessible_to_all:
            with self.subTest(url=url):
                method_func = getattr(self.client, method.lower())
                response = method_func(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_exist_authorized(self):
        """Страницы доступны автору."""
        for url, _, method in UserURLTests.urls_accessible_to_authorized:
            with self.subTest(url=url):
                method_func = getattr(self.authorized_client, method.lower())
                response = method_func(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_redirect_anonymous(self):
        """Страницы перенаправят анонимного пользователя на страницу логина."""
        for url, _, method in UserURLTests.urls_accessible_to_authorized:
            with self.subTest(url=url):
                method_func = getattr(self.client, method.lower())
                response = method_func(url, follow=True)
                self.assertRedirects(response, f'/auth/login/?next={url}')

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_urls = (
            *UserURLTests.urls_accessible_to_authorized,
            *UserURLTests.urls_accessible_to_all,
        )
        for url, template, method in templates_urls:
            with self.subTest(url=url):
                method_func = getattr(self.authorized_client, method.lower())
                response = method_func(url)
                self.assertTemplateUsed(response, template)
