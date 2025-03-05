from django.contrib.auth.password_validation import validate_password
from django.core import exceptions as django_exceptions
from rest_framework import serializers


INVALID_USERNAMES = {'me', 'monkey', 'idiot', 'bitch'}


def validate_username(value):
    """Проверка на запрещенное имя."""
    if value in INVALID_USERNAMES:
        raise serializers.ValidationError(
            'Данное имя пользователя в списке запрещенных имен!'
        )
    return value


class PasswordValidationError(serializers.ValidationError):
    """Кастомная ошибка валидации пароля."""


def validate_new_password(new_password, current_password=None):
    """
    Проверяет новый пароль:
    - Должен отличаться от текущего.
    - Должен соответствовать требованиям Django.
    """
    if current_password and new_password == current_password:
        raise PasswordValidationError("Новый пароль должен отличаться от текущего.")

    try:
        validate_password(new_password)
    except django_exceptions.ValidationError as e:
        raise PasswordValidationError(e.messages)

    return new_password
