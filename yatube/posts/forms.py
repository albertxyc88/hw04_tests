from django import forms

from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ('text', 'group', 'image')
        labels = {'text': 'Текст поста', 'group': 'Group', 'image': 'Картинка'}
        help_texts = {'text': 'Текст нового поста.',
                      'group': 'Группа поста.', }
