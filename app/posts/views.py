from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.views import generic

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post, User
from .utils import paginate


class IndexView(generic.ListView):
    model = Post
    template_name = 'posts/index.html'
    queryset = Post.objects.select_related('group', 'author')
    paginate_by = settings.POSTS_PER_PAGE


class GroupView(generic.ListView):
    model = Post
    template_name = 'posts/group_list.html'
    paginate_by = settings.POSTS_PER_PAGE

    def setup(self, request, slug):
        super().setup(request)
        self.group = get_object_or_404(Group, slug=slug)

    def get_queryset(self):
        return self.group.posts.select_related('author')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['group'] = self.group
        return context


class ProfileView(generic.ListView):
    model = Post
    template_name = 'posts/profile.html'
    paginate_by = settings.POSTS_PER_PAGE

    def setup(self, request, username):
        super().setup(request)
        self.author = get_object_or_404(User, username=username)
        self.following = (
            self.request.user.is_authenticated
            and self.author.following.filter(user=self.request.user).exists()
        )

    def get_queryset(self):
        return self.author.posts.select_related('group')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['author'] = self.author
        context['following'] = self.following
        return context


class PostDetail(generic.DetailView):
    model = Post
    template_name = 'posts/post_detail.html'
    pk_url_kwarg = 'post_id'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = self.object.comments.all()
        context['form'] = CommentForm()
        return context


class PostCreate(LoginRequiredMixin, generic.CreateView):
    form_class = PostForm
    template_name = 'posts/create_post.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('posts:profile', args=[self.request.user.username])


class PostEdit(LoginRequiredMixin, UserPassesTestMixin, generic.UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'posts/create_post.html'
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            post = self.get_object()
            return redirect(post)
        return super().handle_no_permission()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['is_edit'] = True
        return context


class PostDelete(LoginRequiredMixin, UserPassesTestMixin, generic.DeleteView):
    model = Post
    pk_url_kwarg = 'post_id'

    def test_func(self):
        post = self.get_object()
        return self.request.user == post.author

    def handle_no_permission(self):
        if self.request.user.is_authenticated:
            post = self.get_object()
            return redirect(post)
        return super().handle_no_permission()

    def get_success_url(self):
        return reverse('posts:profile', args=[self.request.user.username])


class AddComment(LoginRequiredMixin, generic.CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        post = get_object_or_404(Post, pk=self.kwargs['post_id'])
        form.instance.author = self.request.user
        form.instance.post = post
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('posts:profile', args=[self.request.user.username])


@login_required
def follow_index(request):
    posts = Post.objects.filter(
        author__following__user=request.user
    ).select_related('group', 'author')
    context = {
        'page_obj': paginate(request, posts),
    }
    return render(request, 'posts/follow.html', context)


@login_required
def profile_follow(request, username):
    author = get_object_or_404(User, username=username)
    if request.user != author:
        Follow.objects.get_or_create(user=request.user, author=author)
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    subscription = author.following.filter(user=request.user)  # type: ignore
    subscription.delete()
    return redirect('posts:profile', username=username)
