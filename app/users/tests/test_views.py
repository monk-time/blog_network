from django.forms import fields
from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User

from ..forms import CreationForm


class UserViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        cls.urls_accessible_to_all = (
            (reverse('users:signup'), 'users/signup.html', 'GET'),
            (reverse('users:login'), 'users/login.html', 'GET'),
            (
                reverse('users:password_reset'),
                'users/password_reset.html',
                'GET',
            ),
            (
                reverse('users:password_reset_done'),
                'users/password_reset_done.html',
                'GET',
            ),
            (
                reverse(
                    'users:password_reset_confirm',
                    kwargs={'uidb64': '123', 'token': '123'},
                ),
                'users/password_reset_confirm.html',
                'GET',
            ),
            (
                reverse('users:password_reset_complete'),
                'users/password_reset_complete.html',
                'GET',
            ),
            (reverse('users:logout'), 'users/logged_out.html', 'POST'),
        )
        cls.urls_accessible_to_authorized = (
            (
                reverse('users:password_change'),
                'users/password_change.html',
                'GET',
            ),
            (
                reverse('users:password_change_done'),
                'users/password_change_done.html',
                'GET',
            ),
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UserViewTests.user)

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_urls = (
            *UserViewTests.urls_accessible_to_authorized,
            *UserViewTests.urls_accessible_to_all,
        )
        for url, template, method in templates_urls:
            with self.subTest(url=url):
                method_func = getattr(self.authorized_client, method.lower())
                response = method_func(url)
                self.assertTemplateUsed(response, template)

    def test_signup_page_has_correct_context(self):
        """Страница регистрации сформирована с правильным контекстом."""
        response = self.client.get(reverse('users:signup'))
        form_fields = ['first_name', 'last_name', 'username', 'email']

        self.assertIsInstance(response.context['form'], CreationForm)
        for field in form_fields:
            with self.subTest(field=field):
                form_field = response.context['form'].fields[field]
                self.assertIsInstance(form_field, fields.CharField)
