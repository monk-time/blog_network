from django.http import HttpRequest, HttpResponse


def index(request: HttpRequest):
    return HttpResponse('Главная страница социальной сети блогеров Yatube')


def group_posts(request: HttpRequest, slug: str):
    return HttpResponse(f'Посты группы "{slug}"')
