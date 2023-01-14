from django.http import HttpRequest
from django.shortcuts import render


def index(request: HttpRequest):
    template = 'posts/index.html'
    context = {'title': 'Это главная страница проекта Yatube'}
    return render(request, template, context)


def group_posts(request: HttpRequest, slug: str):
    template = 'posts/group_list.html'
    context = {'title': 'Здесь будет информация о группах проекта Yatube'}
    return render(request, template, context)
