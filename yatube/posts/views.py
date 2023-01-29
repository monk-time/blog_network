from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.core.paginator import Page, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User


def paginate(request: HttpRequest, posts) -> Page:
    """Разбить набор постов на страницы и вернуть запрашиваемую страницу."""
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request: HttpRequest):
    posts = Post.objects.select_related('group', 'author')
    context = {'page_obj': paginate(request, posts)}
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')  # type: ignore
    context = {
        'group': group,
        'page_obj': paginate(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request: HttpRequest, username: str):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('group')  # type: ignore
    context = {
        'author': user,
        'page_obj': paginate(request, posts),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    return render(request, 'posts/post_detail.html', {'post': post})


@login_required
def post_create(request: HttpRequest):
    template = 'posts/create_post.html'
    if request.method != 'POST':
        return render(request, template, {'form': PostForm()})

    post = Post(author=request.user)
    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        return render(request, template, {'form': form})

    form.save()
    return redirect('posts:profile', username=request.user.username)


@login_required
def post_edit(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect('posts:post_detail', post_id=post_id)

    template = 'posts/create_post.html'
    if request.method != 'POST':
        form = PostForm(instance=post)
        return render(request, template, {'form': form, 'is_edit': True})

    form = PostForm(request.POST, instance=post)
    if not form.is_valid():
        return render(request, template, {'form': form, 'is_edit': True})

    form.save()
    return redirect('posts:post_detail', post_id=post_id)
