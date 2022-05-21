from django.contrib.auth import get_user_model
from django.test import TestCase

from ..models import Group, Post

User = get_user_model()
# Limit for __str__ method Post text field
LIMIT_STR: int = 15


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост Тестовый пост Тестовый пост Тестовый пост',
        )

    def test_titles(self):
        """Проверяем, что у моделей корректно работает __str__."""
        models = {
            'group': 'title',
            'post': 'text',
        }
        for model, element in models.items():
            with self.subTest(model=model):
                expect_model = getattr(PostModelTest, model)
                expect_element = getattr(expect_model, element)
                if model == 'post':
                    self.assertEqual(
                        str(expect_model),
                        expect_element[:LIMIT_STR]
                    )
                else:
                    self.assertEqual(str(expect_model), expect_element)

    def test_help_text_post(self):
        """Проверяем, что у модели post у каждого поля указаны help_text."""
        post = PostModelTest.post
        field_help_texts = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор поста',
            'group': 'Группа поста',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value)

    def test_help_text_group(self):
        """Проверяем, что у модели group у каждого поля указаны help_text."""
        group = PostModelTest.group
        field_help_texts = {
            'title': 'Название группы',
            'slug': 'Адрес страницы',
            'description': 'Описание группы',
        }
        for field, expected_value in field_help_texts.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value)

    def test_verbose_name_post(self):
        """Проверяем, что у модели post у каждого поля указан verbose_name."""
        post = PostModelTest.post
        field_verbose_names = {
            'text': 'Текст',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа',
        }
        for field, expected_value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value)

    def test_verbose_name_group(self):
        """Проверяем, что у модели group у каждого поля указан verbose_name."""
        group = PostModelTest.group
        field_verbose_names = {
            'title': 'Название',
            'slug': 'url',
            'description': 'Описание',
        }
        for field, expected_value in field_verbose_names.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value)
