# posts/tests/test_urls.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostsURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост Тестовый пост Тестовый пост',
        )

    def setUp(self):
        # Создаем неавторизованный клиент
        self.guest_client = Client()
        # Создаем второй клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)
        # Создаем еще одного клиента, пригодится для
        # проверки редактирования поста авторизованным не автором.
        self.user_two = User.objects.create_user(username='TestUser')
        self.authorized_client_two = Client()
        # Авторизуем пользователя.
        self.authorized_client_two.force_login(self.user_two)

    def test_pages_url_exists(self):
        """Проверка доступных всем страниц."""
        check_pages = (
            '/',
            '/group/test_group/',
            '/profile/HasNoName/',
            f'/posts/{self.post.id}/',
        )
        for page in check_pages:
            with self.subTest(page=page):
                response = self.guest_client.get(page)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page_as_user_edit_page_as_author(self):
        """Проверяем на доступность страницу /create/
        авторизованным пользователем.
        Страницу редактирования поста автором поста.
        """
        check_pages = (
            '/create/',
            f'/posts/{self.post.id}/edit/',
        )
        for page in check_pages:
            response = self.authorized_client.get(page)
            self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_create_page_as_guest(self):
        """Проверяем страницу /create/: Гостя - перенаправляем."""
        response = self.guest_client.get('/create/')
        self.assertRedirects(response, ('/auth/login/?next=/create/'))

    def test_edit_page_as_non_author(self):
        """Проверим редирект при попытке редактировать пост
        гостем или не автором.
        """
        users_urls = {
            'guest_client': f'/auth/login/?next=/posts/'
                            f'{self.post.id}/edit/',
            'authorized_client_two': f'/posts/{self.post.id}/',
        }
        for user, url in users_urls.items():
            with self.subTest(user=user):
                response = getattr(self, user)
                response = response.get(f'/posts/{self.post.id}/edit/')
                self.assertRedirects(response, url)

    def test_unexisting_page(self):
        """Проверка наличия ошибки несуществующей страницы."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_check_page_templates(self):
        """Проверяем корректность шаблонов у страниц."""
        pages = {
            '/': 'posts/index.html',
            '/group/test_group/': 'posts/group_list.html',
            '/profile/HasNoName/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
        }
        for page, template in pages.items():
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                self.assertTemplateUsed(response, template)

    def test_add_comment_as_guest(self):
        """Проверяем работу добавления комментария /posts/id/comment/:
        Гостю не даем публиковать - перенаправляем на авторизацию."""
        response = self.guest_client.get(f'/posts/{self.post.id}/comment/')
        self.assertRedirects(
            response,
            (f'/auth/login/?next=/posts/{self.post.id}/comment/')
        )
