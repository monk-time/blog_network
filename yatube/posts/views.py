from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from yatube.settings import POSTS_PER_PAGE

from .models import Group, Post


def index(request: HttpRequest):
    posts = Post.objects.all()[:POSTS_PER_PAGE]
    context = {'posts': posts}
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()[:POSTS_PER_PAGE]  # type: ignore
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
