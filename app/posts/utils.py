from django.conf import settings
from django.core.paginator import Page, Paginator
from django.db.models.query import QuerySet
from django.http import HttpRequest


def paginate(request: HttpRequest, posts: QuerySet) -> Page:
    """Разбить набор постов на страницы и вернуть запрашиваемую страницу."""
    paginator = Paginator(posts, settings.POSTS_PER_PAGE)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)
