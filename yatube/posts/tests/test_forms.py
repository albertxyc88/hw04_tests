# posts/tests/tests_forms.py
import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse
from posts.models import Comment, Group, Post

User = get_user_model()

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsCreateFormTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_group',
            description='Тестовое описание',
        )
        cls.group_two = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_group_two',
            description='Тестовое описание 2',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с группой',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_creating_new_post(self):
        """Проверка создания нового поста с группой и картинкой."""
        posts_count = Post.objects.count()
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
        form_data = {
            'text': 'Новый текст очередного поста.',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', kwargs={'username': self.user})
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        latest = Post.objects.order_by('-pub_date').first()
        self.assertEqual(latest.pk, posts_count + 1)
        self.assertEqual(latest.text, form_data['text'])
        self.assertEqual(latest.group, self.group)
        self.assertEqual(latest.image, 'posts/small.gif')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_editing_existing_post(self):
        """Проверка редактирования поста с новым текстом и группой."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст поста',
            'group': self.group_two.id
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.context.get('post').text, form_data['text'])
        self.assertEqual(
            response.context.get('post').group.id,
            form_data['group']
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_adding_comment(self):
        """Проверяем что комментарий после добавления появляется
        на странице подброной информации поста."""
        comments_count = Comment.objects.filter(post=self.post.id).count()
        form_data = {
            'text': 'Новый комментарий',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post.id).count(),
            comments_count + 1)
        latest = (
            Comment
            .objects
            .filter(post=self.post.id)
            .order_by('-pub_date')
            .first()
        )
        self.assertEqual(latest.pk, comments_count + 1)
        self.assertEqual(latest.text, form_data['text'])
        self.assertEqual(response.status_code, HTTPStatus.OK)
