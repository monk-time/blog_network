from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post, User


class PostFormTests(TestCase):
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
        cls.post = Post.objects.create(
            text='Заранее созданный пост',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

    def test_post_form_creates_new_post(self):
        """При отправке валидной формы создаётся новый пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Созданный через форму пост',
            'group': str(PostFormTests.group.pk),
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[PostFormTests.user.username]),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                author=PostFormTests.user,
                group=PostFormTests.group,
            ).exists()
        )

    def test_post_form_edits_existing_post(self):
        """При отправке валидной формы редактируется существующий пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост',
            'group': str(PostFormTests.group.pk),
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.pk]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, PostFormTests.post.get_absolute_url())
        self.assertEqual(Post.objects.count(), posts_count)
        PostFormTests.post.refresh_from_db()
        self.assertEqual(PostFormTests.post.text, form_data['text'])
        self.assertEqual(PostFormTests.post.group, PostFormTests.group)
