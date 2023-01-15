from django.http import HttpRequest
from django.shortcuts import get_object_or_404, render

from .models import Group, Post


def index(request: HttpRequest):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts,
        'title': 'Последние обновления на сайте',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    group = get_object_or_404(Group, slug=slug)
    posts = Post.objects.filter(group=group).order_by('-pub_date')[:10]
    title = f'Записи сообщества "{group.title}"'
    context = {
        'group': group,
        'posts': posts,
        'title': title,
    }
    return render(request, 'posts/group_list.html', context)
