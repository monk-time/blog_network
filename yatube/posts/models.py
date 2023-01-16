from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Group(models.Model):
    title = models.CharField("group's title", max_length=200)
    slug = models.SlugField('readable part of the URL', unique=True)
    description = models.TextField('information about the group')

    def __str__(self):
        return self.title


class Post(models.Model):
    text = models.TextField("post's content")
    pub_date = models.DateTimeField('publication date', auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts',
        verbose_name="post's author",
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.CASCADE,
        related_name='posts',
        blank=True,
        null=True,
        verbose_name='related group',
    )
