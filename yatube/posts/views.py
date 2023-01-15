from django.http import HttpRequest
from django.shortcuts import render

from .models import Post


def index(request: HttpRequest):
    posts = Post.objects.order_by('-pub_date')[:10]
    context = {
        'posts': posts,
        'title': 'Это главная страница проекта Yatube',
    }
    return render(request, 'posts/index.html', context)


def group_posts(request: HttpRequest, slug: str):
    template = 'posts/group_list.html'
    context = {'title': 'Здесь будет информация о группах проекта Yatube'}
    return render(request, template, context)
