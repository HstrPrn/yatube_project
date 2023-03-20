from django.db import models
from django.contrib.auth import get_user_model


SHOWN_CHARS_COUNT = 15

User = get_user_model()


class Group(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(max_length=200)
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts',
    )

    def __str__(self):
        return self.text[:SHOWN_CHARS_COUNT]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'
