from http import HTTPStatus

from django.test import Client, TestCase


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

    def setUp(self):
        self.guest_client = Client()

    def test_about_urls_exist(self):
        """Страницы /about/.../ доступны любому пользователю."""
        for url in AboutURLTests.urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        for url, template in AboutURLTests.urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertTemplateUsed(response, template)