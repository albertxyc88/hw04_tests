# posts/tests/tests_forms.py
from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from posts.models import Group, Post

User = get_user_model()


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

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_creating_new_post(self):
        """Проверка создания нового поста с группой."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст очередного поста.',
            'group': self.group.id,
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
        self.assertTrue(
            Post.objects.filter(
                text='Новый текст очередного поста.',
                group=self.group.id
            ).exists()
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_check_editing_existing_post(self):
        """Проверка редактирования поста с новым текстом и группой"""
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
