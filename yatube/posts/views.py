from django.contrib.auth.decorators import login_required
from django.http import HttpRequest
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.cache import cache_page

from .forms import CommentForm, PostForm
from .models import Follow, Group, Post, User
from .utils import paginate


@cache_page(20, key_prefix='index_page')
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
    author = get_object_or_404(User, username=username)
    posts = author.posts.select_related('group')  # type: ignore
    following = (
        request.user.is_authenticated
        and Follow.objects.filter(user=request.user, author=author).exists()
    )
    context = {
        'author': author,
        'page_obj': paginate(request, posts),
        'following': following,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request: HttpRequest, post_id: int):
    post = get_object_or_404(Post, pk=post_id)
    context = {
        'post': post,
        'comments': post.comments.all(),  # type: ignore
        'form': CommentForm(),
    }
    return render(request, 'posts/post_detail.html', context)


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


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect(post)


@login_required
def follow_index(request):
    subscribed_to = [follow.author for follow in request.user.follower.all()]
    posts = Post.objects.filter(author__in=subscribed_to)
    context = {
        'page_obj': paginate(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    not_already_subscribed = not Follow.objects.filter(
        user=request.user, author=author
    ).exists()
    if not_already_subscribed and request.user.username != username:
        Follow.objects.create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    subscription = Follow.objects.filter(user=request.user, author=author)
    if subscription.exists():
        subscription.delete()
    return redirect('posts:profile', username=username)
