from django.conf import settings
from django.core.paginator import Page, Paginator
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Group, Post, User


def paginate(request: HttpRequest, posts) -> Page:
    """Разбить набор постов на страницы и вернуть запрашиваемую страницу."""
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def index(request: HttpRequest):
    posts = Post.objects.select_related('group', 'author')
    context = {'page': paginate(request, posts)}
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.select_related('author')  # type: ignore
    context = {
        'group': group,
        'page': paginate(request, posts),
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = user.posts.select_related('group')  # type: ignore
    context = {
        'user': user,
        'page': paginate(request, posts),
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    context = {'post': post}
    return render(request, 'posts/post_detail.html', context)
