from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render

from .addons import paginator
from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User

# Numbers of title length
TITLE_LENGTH: int = 30


def index(request):
    template = 'posts/index.html'
    title = "Последние обновления на сайте"
    posts = Post.objects.select_related('author', 'group').all()
    page_obj = paginator(request, posts)
    context = {
        'title': title,
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
        'page_obj': page_obj,
    }
    return render(request, template, context)


def profile(request, username):
    template = 'posts/profile.html'
    author = get_object_or_404(User, username=username)
    title = f'Профайл пользователя { author.get_full_name() }'
    posts = Post.objects.select_related(
                'author', 'group'
            ).filter(author=author)
    count = posts.count()
    page_obj = paginator(request, posts)
    if request.user.is_authenticated:
        following = Follow.objects.filter(
                user=request.user, author=author
            ).exists()
    else:
        following = False
    if request.user == author:
        user_not_author = True
    else:
        user_not_author = False
    context = {
        'author': author,
        'title': title,
        'page_obj': page_obj,
        'count': count,    
        'following': following,
        'user_not_author': user_not_author,
    }
    return render(request, template, context)


def post_detail(request, post_id):
    template = 'posts/post_detail.html'
    post = Post.objects.get(pk=post_id)
    title = post.text[:TITLE_LENGTH]
    count = Post.objects.filter(author=post.author).count()
    form = CommentForm()
    comments = Comment.objects.select_related('author').filter(post=post.id)
    context = {
        'post_id': post_id,
        'post': post,
        'count': count,
        'title': title,
        'comments': comments,
        'form': form,
    }
    return render(request, template, context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        form.instance.author = request.user
        form.instance.post = post
        form.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    title = 'Добавить запись'
    form = PostForm(
        request.POST or None,
        request.FILES or None,
    )
    if form.is_valid():
        text = form.cleaned_data['text']
        group = form.cleaned_data['group']
        image = form.cleaned_data['image']
        author = request.user
        Post.objects.create(text=text, author=author, group=group, image=image)
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
    form = PostForm(
        instance=post,
        data=request.POST or None,
        files=request.FILES or None,
    )
    if form.is_valid():
        form.save()
        return redirect('posts:post_detail', post_id=post_id)
    context = {
        'title': title,
        'form': form,
        'is_edit': is_edit,
    }
    return render(request, template, context)


@login_required
def follow_index(request):
    template = 'posts/follow.html'
    title = "Последние обновления авторов"
    posts = Post.objects.filter(author__following__user=request.user)
    page_obj = paginator(request, posts)
    context = {
        'title': title,
        'page_obj': page_obj,
    }
    return render(request, template, context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    user = request.user
    author = get_object_or_404(User, username=username)
    follower_count = Follow.objects.filter(user=user, author=author).count()
    if user != author and follower_count == 0:
        Follow.objects.create(user=user, author=author)
    return redirect('posts:profile', username=author)


@login_required
def profile_unfollow(request, username):
    # Отписаться от автора
    author = get_object_or_404(User, username=username)
    follower = Follow.objects.filter(user=request.user, author=author)
    if follower.exists():
        follower.delete()
    return redirect('posts:profile', username=author)
