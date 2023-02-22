from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render

from .forms import PostForm
from .models import Group, Post, User
from .utils import paginate


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
    post = Post(author=request.user)
    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(request, 'posts/create_post.html', {'form': form})

    form.save()
    return redirect(
        'posts:profile', username=request.user.username  # type: ignore
    )


@login_required
def post_edit(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(post)

    form = PostForm(
        request.POST or None,
        instance=post,
        files=request.FILES or None,
    )
    if not form.is_valid():
        return render(
            request, 'posts/create_post.html', {'form': form, 'is_edit': True}
        )

    form.save()
    return redirect(post)


@login_required
def post_delete(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    if request.user != post.author:
        return redirect(post)

    post.delete()
    return redirect(
        'posts:profile', username=request.user.username  # type: ignore
    )
