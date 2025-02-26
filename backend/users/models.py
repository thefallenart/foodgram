from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    """Кастомная модель пользователя для проекта Foodgram."""

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    email = models.EmailField(
        max_length=254,
        verbose_name='Адрес электронной почты',
        unique=True,
        error_messages={
            'unique': 'Данный адрес уже используется',
        },
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True,
        db_index=True,
        error_messages={
            'unique': 'Пользователь с таким именем уже существует',
        },
    )
    first_name = models.CharField(
        max_length=150,
        verbose_name='Имя',
        help_text='Ваше имя (например, Иван).'
    )
    last_name = models.CharField(
        max_length=150,
        verbose_name='Фамилия',
        help_text='Ваша фамилия (например, Иванов).'
    )
    avatar = models.ImageField(
        upload_to='avatars/',
        verbose_name='Аватар',
        blank=True,
        null=True
    )

    class Meta:
        """Настройки модели пользователя."""

        ordering = ('username',)
        verbose_name = 'Учетная запись'
        verbose_name_plural = 'Учетные записи'

    def __str__(self):
        """Возвращает строковое представление пользователя."""

        return self.username
