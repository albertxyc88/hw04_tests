# posts/tests/tests_forms.py
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
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с группой',
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_check_creating_new_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст поста из формы',
            'slug': self.group
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count+1)
        self.assertEqual(response.status_code, 200)

    def test_check_editing_existing_post(self):
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Новый текст поста',
            'slug': self.group
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertEqual(response.context.get('post').text, form_data['text'])
        self.assertEqual(response.status_code, 200)
