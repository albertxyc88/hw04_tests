# about/test.py
from http import HTTPStatus

from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        # Создаем неавторизованый клиент
        self.guest_client = Client()

    def test_static_pages_url_exists(self):
        """Проверка доступности адресов статичных страниц."""
        check_pages = ('/about/author/', '/about/tech/')
        for page in check_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_static_pages_template(self):
        """Проверка правильности шаблонов статичных страниц."""
        check_pages = {
            '/about/tech/': 'about/tech.html',
            '/about/author/': 'about/author.html',
        }
        for page, template in check_pages.items():
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertTemplateUsed(response, template)
