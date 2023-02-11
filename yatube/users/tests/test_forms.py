from django.test import Client, TestCase
from django.urls import reverse

from posts.models import User


class UserFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.form_data = {
            'first_name': 'Test',
            'last_name': 'User',
            'username': 'test_user',
            'email': 'test@test.com',
            'password1': 'testpassword',
            'password2': 'testpassword',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_user_signing_up_creates_new_user(self):
        users_count = User.objects.count()
        response = self.guest_client.post(
            reverse('users:signup'), data=UserFormTests.form_data, follow=True
        )
        self.assertRedirects(response, reverse('posts:index'))
        self.assertEqual(User.objects.count(), users_count + 1)
        self.assertTrue(User.objects.filter(username='test_user').exists())

    def test_user_cant_signup_with_registered_email(self):
        self.guest_client.post(
            reverse('users:signup'), data=UserFormTests.form_data
        )
        users_count = User.objects.count()
        response = self.guest_client.post(
            reverse('users:signup'), data=UserFormTests.form_data
        )
        self.assertEqual(User.objects.count(), users_count)
        self.assertFormError(
            response,
            form='form',
            field='email',
            errors='Этот адрес уже зарегистрирован',
        )
