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
        cls.urls_accessible_to_all = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_reset'): 'users/password_reset.html',
            reverse(
                'users:password_reset_done'
            ): 'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={'uidb64': '123', 'token': '123'},
            ): 'users/password_reset_confirm.html',
            reverse(
                'users:password_reset_complete'
            ): 'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }
        cls.urls_accessible_to_authorized = {
            reverse('users:password_change'): 'users/password_change.html',
            reverse(
                'users:password_change_done'
            ): 'users/password_change_done.html',
        }

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(UserViewTests.user)

    def test_urls_use_correct_template(self):
        """URL-адреса используют соответствующие шаблоны."""
        templates_urls = {
            **UserViewTests.urls_accessible_to_authorized,
            **UserViewTests.urls_accessible_to_all,
        }
        for url, template in templates_urls.items():
            with self.subTest(url=url):
                response = self.authorized_client.get(url)
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
