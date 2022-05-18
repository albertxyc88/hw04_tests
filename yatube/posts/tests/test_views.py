# posts/tests/test_views.py
import shutil
import tempfile

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)

# Количество создаваемых постов для теста должно быть меньше от 11 до 20.
CREATE_POST: int = 20

# Для title на странице post_detail ограничение в 30 символов.
TITLE_LENGTH: int = 30


@override_settings (MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        small_gif = (            
             b'\x47\x49\x46\x38\x39\x61\x02\x00'
             b'\x01\x00\x80\x00\x00\x00\x00\x00'
             b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
             b'\x00\x00\x00\x2C\x00\x00\x00\x00'
             b'\x02\x00\x01\x00\x00\x02\x02\x0C'
             b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с группой и с длинным текстом',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

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
                self.assertEqual(response.context['page_obj'][0], self.post)

    def test_post_detail_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        count = Post.objects.filter(author=self.post.author).count()
        title = self.post.text[:TITLE_LENGTH]
        self.assertEqual(response.context['post'], self.post)
        self.assertEqual(response.context['title'], title)
        self.assertEqual(response.context['count'], count)
        self.assertEqual(response.context['image'], 'posts/small.gif')

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
        for form in check_forms:
            self.assertIsInstance(form.context['form'], PostForm)


class PaginatorViewsTest(TestCase):
    """Проверяем paginator на страницах"""
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Paginator')
        cls.group = Group.objects.create(
            title='Группа paginator',
            slug='paginator_group',
            description='Описание для группы paginator',
        )
        Post.objects.bulk_create(
            [
                Post(
                    text=f'{i} - Тестовый пост с группой.',
                    author=cls.user,
                    group=cls.group,
                )
                for i in range(CREATE_POST)
            ]
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
                    kwargs={'username': self.user.username}),
        )
        for page in check_pages:
            response = self.client.get(page)
            # Проверка: количество постов на первой странице равно 10.
            self.assertEqual(
                len(response.context['page_obj']),
                settings.POSTS_ON_PAGE
            )

    def test_second_page_contains_three_records(self):
        check_pages = (
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.group.slug}),
            reverse('posts:profile',
                    kwargs={'username': self.user.username}),
        )
        # Проверка: на второй странице должно быть три поста.
        for page in check_pages:
            response = self.client.get(page + '?page=2')
            self.assertEqual(
                len(response.context['page_obj']),
                CREATE_POST - settings.POSTS_ON_PAGE
            )
