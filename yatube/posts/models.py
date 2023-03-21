from django.db import models
from django.contrib.auth import get_user_model
from core.models import CreatedModel


SHOWN_CHARS_COUNT = 15

User = get_user_model()


class Group(models.Model):
    title = models.CharField(
        'Название группы',
        max_length=200
    )
    slug = models.SlugField(unique=True)
    description = models.TextField()

    def __str__(self):
        return f'{self.title}'

    class Meta:
        verbose_name = 'Группа'
        verbose_name_plural = 'Группы'


class Post(models.Model):
    text = models.TextField(
        'Текст поста',
        help_text='Текст нового поста',
        max_length=200
    )
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
        verbose_name='Группа',
        help_text='Группа, к которой будет относиться пост',
        related_name='posts',
    )
    image = models.ImageField(
        'Картинка',
        help_text='Картинка поста',
        upload_to='posts/',
        blank=True
    )

    def __str__(self):
        return self.text[:SHOWN_CHARS_COUNT]

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Пост'
        verbose_name_plural = 'Посты'


class Comment(CreatedModel):
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        blank=True,
        null=True,
        related_name='comments'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='comments'
    )
    text = models.TextField(
        'Текст комментария',
        help_text='Твое мнение очень важно для автора',
        max_length=400
    )

    def __str__(self):
        return f'Комментарий от {self.author} к посту {self.post}'

    class Meta:
        ordering = ['created']
        verbose_name = 'Комментарий'
        verbose_name_plural = 'Комментарии'
