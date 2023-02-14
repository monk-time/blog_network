from django.conf import settings
from django.forms import fields
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.group_without_posts = Group.objects.create(
            title='Группа без постов',
            slug='empty-group',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(PostPagesTests.user)

    def test_pages_use_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTests.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username},
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', kwargs={'post_id': PostPagesTests.post.pk}
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', kwargs={'post_id': PostPagesTests.post.pk}
            ): 'posts/create_post.html',
        }
        for url, template in urls.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def post_check(self, post):
        """Проверить, что объект поста равен изначальному посту."""
        self.assertEqual(post.pk, PostPagesTests.post.pk)
        self.assertEqual(post.text, PostPagesTests.post.text)
        self.assertEqual(post.author.username, PostPagesTests.user.username)
        self.assertEqual(post.group.slug, PostPagesTests.group.slug)

    def test_index_has_correct_context(self):
        """Главная страница сформирована с правильным контекстом."""
        response = self.guest_client.get(reverse('posts:index'))
        self.post_check(response.context['page_obj'][0])

    def test_group_list_has_correct_context(self):
        """Страница группы сформирована с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list', kwargs={'slug': PostPagesTests.group.slug}
            )
        )
        self.post_check(response.context['page_obj'][0])
        self.assertEqual(response.context['group'], PostPagesTests.group)

    def test_profile_has_correct_context(self):
        """Страница профиля сформирована с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': PostPagesTests.user.username},
            )
        )
        self.post_check(response.context['page_obj'][0])
        self.assertEqual(response.context['author'], PostPagesTests.user)

    def test_post_detail_has_correct_context(self):
        """Страница поста сформирована с правильным контекстом."""
        response = self.guest_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': PostPagesTests.post.pk},
            )
        )
        self.post_check(response.context['post'])

    def test_post_create_form_has_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_form_has_correct_context(self):
        """Страница редактирования поста сформирована с правильным
        контекстом.
        """
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': PostPagesTests.post.pk},
            )
        )
        self.post_check(response.context['form'].instance)

    def test_post_group_contains_only_correct_posts(self):
        """Посты не попают в группу, для которой они не предназначены."""
        response = self.guest_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPagesTests.group_without_posts.slug},
            )
        )
        posts = response.context['page_obj']
        self.assertEqual(len(posts), 0)


class PostPaginatorTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(  # type: ignore
            username='test_user'
        )
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.POSTS_CREATED = settings.POSTS_PER_PAGE + 3
        posts = [
            Post(
                text='Тестовый пост',
                author=cls.user,
                group=cls.group,
            )
            for _ in range(cls.POSTS_CREATED)
        ]
        Post.objects.bulk_create(posts)
        # bulk_create doesn't call save(), so pk are not set yet
        cls.posts = Post.objects.all()

    def test_paginated_pages_show_correct_post_count(self):
        """Страницы с пагинатором выводят корректное кол-во постов."""
        total = PostPaginatorTests.POSTS_CREATED
        per_page = settings.POSTS_PER_PAGE
        paginated_urls = [
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': PostPaginatorTests.group.slug},
            ),
            reverse(
                'posts:profile',
                kwargs={'username': PostPaginatorTests.user.username},
            ),
        ]
        for url in paginated_urls:
            with self.subTest(url=url):
                response = self.client.get(url)
                posts = response.context['page_obj']
                num_posts_on_first_page = min(total, per_page)
                self.assertEqual(len(posts), num_posts_on_first_page)

                if total < per_page:
                    return
                response = self.client.get(url + '?page=2')
                posts = response.context['page_obj']
                num_posts_on_second_page = min(total - per_page, per_page)
                self.assertEqual(len(posts), num_posts_on_second_page)
