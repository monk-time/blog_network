from django.conf import settings
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Group, Post


def index(request: HttpRequest):
    posts = Post.objects.select_related('group')[: settings.POSTS_PER_PAGE]
    context = {'posts': posts}
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[: settings.POSTS_PER_PAGE]  # type: ignore
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
