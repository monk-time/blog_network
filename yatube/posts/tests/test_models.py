from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')  # type: ignore
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.short_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.long_post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост с очень длинным содержимым',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        post = PostModelTest.short_post
        self.assertEqual(str(post), 'Тестовый пост')
        post = PostModelTest.long_post
        self.assertEqual(str(post), 'Тестовый пост с')
        group = PostModelTest.group
        self.assertEqual(str(group), 'Тестовая группа')
