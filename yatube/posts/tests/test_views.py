# posts/tests/test_views.py
from django import forms
from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostsPagesTests(TestCase):
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
            text='Тестовый пост с группой',
            group=cls.group,
        )

    def setUp(self):
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        template_pages = {
            reverse('posts:index'): 'posts/index.html',
            (
                reverse(
                    'posts:group_list',
                    kwargs={'slug': self.group.slug}
                )
            ): 'posts/group_list.html',
            (
                reverse(
                    'posts:profile',
                    kwargs={'username': self.post.author.username}
                )
            ): 'posts/profile.html',
            (
                reverse(
                    'posts:post_detail',
                    kwargs={'post_id': self.post.id}
                )
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            (
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id}
                )
            ): 'posts/create_post.html',
        }
        """
        Проверяем, что при обращении к name вызывается
        соответствующий HTML-шаблон
        """
        for reverse_name, template in template_pages.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_having_correct_context(self):
        check_pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}),
        )
        for page in check_pages:
            with self.subTest(page=page):
                response = self.authorized_client.get(page)
                first_object = response.context['page_obj'][0]
                task_author_0 = first_object.author.username
                task_group_0 = first_object.group
                task_text_0 = first_object.text
                self.assertEqual(task_author_0, self.post.author.username)
                self.assertEqual(task_group_0, self.post.group)
                self.assertEqual(task_text_0, self.post.text)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(response.context.get('post').group, self.post.group)
        self.assertEqual(response.context.get('post').author, self.post.author)
        self.assertEqual(response.context.get('post').text, self.post.text)

    def test_create_edit_post_having_correct_form(self):
        check_forms = (
            self.authorized_client.get(reverse('posts:post_create')),
            self.authorized_client.get(
                reverse(
                    'posts:post_edit',
                    kwargs={'post_id': self.post.id}
                )
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for form in check_forms:
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = form.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)


class PaginatorViewsTest(TestCase):
    """Проверяем paginator на страницах"""

    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        for i in range(13):
            cls.post = Post.objects.create(
                author=cls.user,
                text=f'{i} - Тестовый пост с группой.',
                group=cls.group,
            )

    def setUp(self):
        # Создаем клиент
        self.authorized_client = Client()
        # Авторизуем пользователя
        self.authorized_client.force_login(self.user)

    def test_first_page_contains_ten_records(self):
        check_pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}),
        )
        for page in check_pages:
            response = self.client.get(page)
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        check_pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.post.author.username}),
        )
        # Проверка: на второй странице должно быть три поста.
        for page in check_pages:
            response = self.client.get(page + '?page=2')
            self.assertEqual(len(response.context['page_obj']), 3)
