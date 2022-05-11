from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .addons import paginator
from .forms import PostForm
from .models import Group, Post, User

# Numbers of title length
TITLE_LENGTH: int = 30


def index(request):
    template = 'posts/index.html'
    title = "Последние обновления на сайте"
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(request, posts)
    context = {
        'title': title,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    template = 'posts/group_list.html'
    posts = group.posts.select_related('author', 'group').all()
    page_obj = paginator(request, posts)
    context = {
        'group': group,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    posts = (Post.objects.select_related('author', 'group')
             .filter(author=author))
    title = f'Профайл пользователя { author.get_full_name() }'
    page_obj = paginator(request, posts)
    context = {
        'author': author,
        'title': title,
        'posts': posts,
        'page_obj': page_obj,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    title = f'Пост { post.text[:TITLE_LENGTH] }'
    count = Post.objects.filter(author=post.author).count()
    context = {
        'post_id': post_id,
        'post': post,
        'count': count,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    title = 'Добавить запись'
    form = PostForm(request.POST or None)
    if form.is_valid():
        text = form.cleaned_data['text']
        group = form.cleaned_data['group']
        author = request.user
        Post.objects.create(text=text, author=author, group=group)
        return redirect('posts:profile', username=request.user)
    context = {
        'form': form,
        'title': title,
    }
    return render(request, template, context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    template = 'posts/create_post.html'
    if post.author != request.user:
        return redirect('posts:post_detail', post_id=post_id)
    title = 'Редактировать запись'
    is_edit = True
    form = PostForm(instance=post, data=request.POST or None)
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'title': title,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)
