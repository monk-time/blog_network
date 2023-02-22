import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.db.models.fields.files import ImageFieldFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
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
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(PostFormTests.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        self.uploaded_file = SimpleUploadedFile(
            name='small.gif', content=small_gif, content_type='image/gif'
        )

    def test_post_form_creates_new_post(self):
        """При отправке валидной формы создаётся новый пост."""
        Post.objects.all().delete()
        form_data = {
            'text': 'Созданный через форму пост',
            'group': str(PostFormTests.group.pk),
            'image': self.uploaded_file,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'), data=form_data, follow=True
        )
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[PostFormTests.user.username]),
        )
        self.assertEqual(Post.objects.count(), 1)
        post = Post.objects.all()[0]
        self.assertIsInstance(post, Post)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, PostFormTests.group)
        self.assertEqual(post.author, PostFormTests.user)
        self.assertIsInstance(post.image, ImageFieldFile)

    def test_post_form_edits_existing_post(self):
        """При отправке валидной формы редактируется существующий пост."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Отредактированный пост',
            'group': str(PostFormTests.group.pk),
            'image': self.uploaded_file,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[PostFormTests.post.pk]),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, PostFormTests.post.get_absolute_url())
        self.assertEqual(Post.objects.count(), posts_count)
        post = PostFormTests.post
        post.refresh_from_db()
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group, PostFormTests.group)
        self.assertIsInstance(post.image, ImageFieldFile)
