from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse

from blog import constants
from core.models import PublishedModel


User = get_user_model()


class Location(PublishedModel):
    name = models.CharField(
        'Название места',
        max_length=constants.MAX_LENGTH
    )

    class Meta:
        verbose_name = 'местоположение'
        verbose_name_plural = 'Местоположения'
        ordering = ('name',)

    def __str__(self) -> str:
        return self.name[:constants.RECORDS_LIMIT]


class Category(PublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=constants.MAX_LENGTH
    )
    description = models.TextField(
        verbose_name='Описание'
    )
    slug = models.SlugField(
        'Идентификатор',
        unique=True,
        help_text=(
            'Идентификатор страницы для URL; '
            'разрешены символы латиницы, цифры, дефис и подчёркивание.'
        )
    )

    class Meta:
        verbose_name = 'категория'
        verbose_name_plural = 'Категории'
        ordering = ('title',)

    def __str__(self) -> str:
        return self.title[:constants.RECORDS_LIMIT]


class Post(PublishedModel):
    title = models.CharField(
        'Заголовок',
        max_length=constants.MAX_LENGTH
    )
    text = models.TextField(
        verbose_name='Текст'
    )
    pub_date = models.DateTimeField(
        'Дата и время публикации',
        auto_now_add=False,
        help_text=(
            'Если установить дату и время в будущем — '
            'можно делать отложенные публикации.'
        )
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор публикации',
        null=True
    )
    location = models.ForeignKey(
        Location,
        on_delete=models.SET_NULL,
        verbose_name='Местоположение',
        null=True,
        blank=True
    )
    category = models.ForeignKey(
        Category,
        on_delete=models.SET_NULL,
        null=True,
        verbose_name='Категория',
    )
    image = models.ImageField(
        'Изображение',
        upload_to='post_images',
        blank=True,
    )

    class Meta:
        verbose_name = 'публикация'
        verbose_name_plural = 'Публикации'
        default_related_name = 'posts'
        ordering = ('-pub_date', 'title')

    def __str__(self) -> str:
        return self.title[:constants.RECORDS_LIMIT]

    def get_absolute_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.pk})


class Comment(PublishedModel):
    text = models.TextField(
        verbose_name='Текст'
    )
    post = models.ForeignKey(
        Post,
        on_delete=models.CASCADE,
        verbose_name='Пост'
    )
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        verbose_name='Автор'
    )

    class Meta:
        verbose_name = 'коментарий'
        verbose_name_plural = 'Коментарии'
        default_related_name = 'comments'
        ordering = ('created_at',)

    def __str__(self) -> str:
        return (f'Комментарий {self.author} к посту "{self.post}", '
                f'текст: {self.text[:constants.RECORDS_LIMIT]}')
