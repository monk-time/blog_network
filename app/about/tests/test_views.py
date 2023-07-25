from django.test import TestCase
from django.urls import reverse


class AboutViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.urls = {
            reverse('about:author'): 'about/author.html',
            reverse('about:tech'): 'about/tech.html',
        }

    def test_pages_use_correct_template(self):
        """View-функции используют соответствующие шаблоны."""
        for url, template in AboutViewTests.urls.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                self.assertTemplateUsed(response, template)
