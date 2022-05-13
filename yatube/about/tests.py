# about/test.py
from http import HTTPStatus

from django.test import Client, TestCase
from django.urls import reverse


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

    def test_pages_uses_correct_template(self):
        """Проверяем что URL-адрес использует соответствующий шаблон."""
        template_pages = {
            reverse('about:tech'): 'about/tech.html',
            reverse('about:author'): 'about/author.html',
        }
        """Проверяем, что при обращении к name вызывается
        соответствующий HTML-шаблон.
        """
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
