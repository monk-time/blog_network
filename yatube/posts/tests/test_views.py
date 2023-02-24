import shutil
import tempfile

from django.conf import settings
from django.core.cache import cache
from django.core.files.uploadedfile import SimpleUploadedFile
from django.forms import fields
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..forms import PostForm
from ..models import Comment, Follow, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()

        cls.user = User.objects.create_user(username='user1')  # type: ignore
        cls.user2 = User.objects.create_user(username='user2')  # type: ignore
        cls.group = Group.objects.create(
            title='Группа 1',
            slug='slug1',
        )

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )

        cls.post = Post.objects.create(
            text='Тестовый пост',
            author=cls.user,
            group=cls.group,
            image=uploaded,
        )
        cls.comment = Comment.objects.create(
            text='Комментарий',
            author=cls.user,
            post=cls.post,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostViewTests.user)
        self.authorized_client_2 = Client()
        self.authorized_client_2.force_login(PostViewTests.user2)
        cache.clear()

    def test_pages_use_correct_template(self):
        """View-функции используют соответствующие шаблоны."""
        urls = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list', args=[PostViewTests.group.slug]
            ): 'posts/group_list.html',
            reverse(
                'posts:profile', args=[PostViewTests.user.username]
            ): 'posts/profile.html',
            reverse(
                'posts:post_detail', args=[PostViewTests.post.pk]
            ): 'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit', args=[PostViewTests.post.pk]
            ): 'posts/create_post.html',
        }
        for url, template in urls.items():
            with self.subTest(url=url, template=template):
                response = self.authorized_client.get(url)
                self.assertTemplateUsed(response, template)

    def post_check(self, post):
        """Проверить, что объект поста равен изначальному посту."""
        self.assertEqual(post.pk, PostViewTests.post.pk)
        self.assertEqual(post.text, PostViewTests.post.text)
        self.assertEqual(post.author.username, PostViewTests.user.username)
        self.assertEqual(post.group.slug, PostViewTests.group.slug)
        self.assertEqual(post.image, PostViewTests.post.image)

    def test_index_has_correct_context(self):
        """Главная страница сформирована с правильным контекстом."""
        response = self.client.get(reverse('posts:index'))
        self.post_check(response.context['page_obj'][0])

    def test_group_list_has_correct_context(self):
        """Страница группы сформирована с правильным контекстом."""
        response = self.client.get(
            reverse('posts:group_list', args=[PostViewTests.group.slug])
        )
        self.post_check(response.context['page_obj'][0])
        self.assertEqual(response.context['group'], PostViewTests.group)

    def test_profile_has_correct_context(self):
        """Страница профиля сформирована с правильным контекстом."""
        response = self.client.get(
            reverse('posts:profile', args=[PostViewTests.user.username])
        )
        self.post_check(response.context['page_obj'][0])
        self.assertEqual(response.context['author'], PostViewTests.user)

    def test_post_detail_has_correct_context(self):
        """Страница поста сформирована с правильным контекстом."""
        response = self.client.get(PostViewTests.post.get_absolute_url())
        self.post_check(response.context['post'])
        self.assertEqual(
            response.context['comments'][0], PostViewTests.comment
        )

    def test_post_create_form_has_correct_context(self):
        """Страница создания поста сформирована с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': fields.CharField,
            'group': fields.ChoiceField,
            'image': fields.ImageField,
        }

        self.assertIsInstance(response.context['form'], PostForm)
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context['form'].fields[value]
                self.assertIsInstance(form_field, expected)

    def test_post_edit_form_has_correct_context(self):
        """Страница редактирования поста сформирована с правильным
        контекстом.
        """
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[PostViewTests.post.pk])
        )
        self.post_check(response.context['form'].instance)

    def test_pages_contain_only_correct_posts(self):
        """Посты попают только в нужную группу/профиль."""
        post_no_group = Post.objects.create(author=self.user)
        post_by_another_user = Post.objects.create(
            author=self.user2, group=self.group
        )
        group_with_no_posts = Group.objects.create(
            title='Группа 2', slug='slug2'
        )
        expected_posts_by_url = {
            reverse('posts:index'): [
                PostViewTests.post,
                post_by_another_user,
                post_no_group,
            ],
            reverse('posts:group_list', args=[PostViewTests.group.slug]): [
                PostViewTests.post,
                post_by_another_user,
            ],
            reverse('posts:group_list', args=[group_with_no_posts.slug]): [],
            reverse('posts:profile', args=[PostViewTests.user.username]): [
                PostViewTests.post,
                post_no_group,
            ],
            reverse('posts:profile', args=[PostViewTests.user2.username]): [
                post_by_another_user
            ],
        }

        for url, expected_posts in expected_posts_by_url.items():
            with self.subTest(url=url):
                response = self.client.get(url)
                posts = response.context['page_obj']
                self.assertEqual(len(posts), len(expected_posts))
                for post in posts:
                    self.assertIn(post, expected_posts)

    def test_post_can_be_deleted_by_author(self):
        """После удаления автором пост удаляется из базы данных."""
        post_to_delete = Post.objects.create(
            text='Тестовый пост для удаления',
            author=PostViewTests.user,
        )
        posts_count = Post.objects.count()
        self.authorized_client.post(
            reverse('posts:post_delete', args=[post_to_delete.pk])
        )
        self.assertEqual(Post.objects.count(), posts_count - 1)
        self.assertFalse(Post.objects.filter(pk=post_to_delete.pk).exists())

    def test_post_cant_be_deleted_by_wrong_user(self):
        """При попытке удаления неавтором пост остаётся в базе данных."""
        posts_count = Post.objects.count()
        self.authorized_client_2.post(
            reverse('posts:post_delete', args=[PostViewTests.post.pk])
        )
        self.assertEqual(Post.objects.count(), posts_count)
        self.assertTrue(Post.objects.filter(pk=PostViewTests.post.pk).exists())

    def test_index_page_cache(self):
        """Главная страница корректно кэшируется."""
        post = Post.objects.create(
            text='Новый пост',
            author=PostViewTests.user,
        )
        first_response = self.client.get(reverse('posts:index'))
        post.delete()
        cached_response = self.client.get(reverse('posts:index'))
        self.assertEqual(first_response.content, cached_response.content)
        cache.clear()
        noncached_response = self.client.get(reverse('posts:index'))
        self.assertNotEqual(first_response.content, noncached_response.content)

    def test_user_can_subscribe_and_unsubscribe(self):
        """Юзер может подписаться на других юзеров и удалять их из подписок."""
        follow_count = Follow.objects.filter(user=PostViewTests.user).count()
        self.assertEqual(follow_count, 0)
        self.authorized_client.get(
            reverse('posts:profile_follow', args=[PostViewTests.user2])
        )
        follow_count = Follow.objects.filter(user=PostViewTests.user).count()
        self.assertEqual(follow_count, 1)
        self.assertTrue(
            Follow.objects.filter(
                user=PostViewTests.user, author=PostViewTests.user2
            ).exists()
        )
        self.authorized_client.get(
            reverse('posts:profile_unfollow', args=[PostViewTests.user2])
        )
        follow_count = Follow.objects.filter(user=PostViewTests.user).count()
        self.assertEqual(follow_count, 0)

    def test_new_posts_appear_on_subscription_page(self):
        """Новая запись появляется в ленте только тех, кто на него подписан."""
        Follow.objects.create(
            user=PostViewTests.user, author=PostViewTests.user2
        )
        post_by_subscribed_user = Post.objects.create(
            author=PostViewTests.user2, text='пост'
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertEqual(
            response.context['page_obj'][0], post_by_subscribed_user
        )
        response = self.authorized_client_2.get(reverse('posts:follow_index'))
        self.assertEqual(len(response.context['page_obj']), 0)


class PostsPaginatorTests(TestCase):
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
            Post(text='Тестовый пост', author=cls.user, group=cls.group)
            for _ in range(cls.POSTS_CREATED)
        ]
        Post.objects.bulk_create(posts)
        # bulk_create doesn't call save(), so pk are not set yet
        cls.posts = Post.objects.all()

    def test_paginated_pages_show_correct_post_count(self):
        """Страницы с пагинатором выводят корректное кол-во постов."""
        total = PostsPaginatorTests.POSTS_CREATED
        per_page = settings.POSTS_PER_PAGE
        paginated_urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[PostsPaginatorTests.group.slug]),
            reverse('posts:profile', args=[PostsPaginatorTests.user.username]),
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
