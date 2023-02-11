from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


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
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse(
                'posts:profile',
                kwargs={'username': PostFormTests.user.username},
            ),
        )
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Созданный через форму пост',
                author=PostFormTests.user,
                group=PostFormTests.group,
            ).exists()
        )

    def test_post_form_edits_existing_post(self):
        """При отправке валидной формы редактируется существующий пост."""
        form_data = {
            'text': 'Отредактированный пост',
            'group': PostFormTests.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': 1}),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': 1}),
        )
        edited_post = Post.objects.get(id=1)
        self.assertEquals(edited_post.text, 'Отредактированный пост')
        self.assertEquals(edited_post.group, PostFormTests.group)
