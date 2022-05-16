from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()
# Limit for __str__ method Post
LIMIT_STR: int = 15


class Post(models.Model):
    text = models.TextField(
        verbose_name='Текст',
        help_text='Текст поста',
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Дата публикации',
        help_text='Дата публикации поста',
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name='Автор',
        help_text='Автор поста',
    )
    group = models.ForeignKey(
        'Group',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='posts',
        verbose_name='Группа',
        help_text='Группа поста',
    )
    image = models.ImageField(
        'Картинка',
        upload_to='posts/',
        blank=True,
        null=True,
    )

    class Meta:
        ordering = ('-pub_date',)
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'

    def __str__(self):
        return self.text[:LIMIT_STR]


class Group(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name='Название',
        help_text='Название группы',
    )
    slug = models.SlugField(
        max_length=50,
        unique=True,
        verbose_name='url',
        help_text='Адрес страницы',
    )
    description = models.TextField(
        verbose_name='Описание',
        help_text='Описание группы',
    )

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'

    def __str__(self):
        return self.title
