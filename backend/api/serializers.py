import base64
import uuid

from django.core.files.base import ContentFile
from djoser.serializers import UserCreateSerializer, UserSerializer
from rest_framework import serializers

from api.validators import validate_username, validate_new_password
from recipes.models import Ingredient, Recipe, RecipeIngredient, Tag
from users.models import User


MINIMUM = 1
MAXIMUM = 32_000


class Base64ImageField(serializers.ImageField):
    """Кастомное поле для обработки изображений в формате base64."""

    def to_internal_value(self, data):
        if isinstance(data, str) and data.startswith('data:image'):
            format_str, img_str = data.split(';base64,')
            ext = format_str.split('/')[-1]
            data = ContentFile(
                base64.b64decode(img_str),
                name=f'{uuid.uuid4()}.{ext}'
            )
        return super().to_internal_value(data)


class UserCustomCreateSerializer(UserCreateSerializer):
    """Сериализатор для нового пользователя."""
    username = serializers.CharField(validators=[validate_username])

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name',
                  'last_name', 'password')
        extra_kwargs = {'password': {'write_only': True}}


class UserReadSerializer(UserSerializer):
    """Сериализатор для показа пользователей."""
    is_subscribed = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name',
                  'is_subscribed')

    def get_is_subscribed(self, obj):
        """Проверка подписки."""

        request = self.context.get('request')
        if request and not request.user.is_anonymous:
            return request.user.following.filter(author=obj).exists()
        return False


class AvatarSerializer(serializers.ModelSerializer):
    """Сериализатор для обновления аватара пользователя."""

    avatar = Base64ImageField(required=False)

    def validate(self, attrs):
        """Проверяет, что запрос не пуст."""
        if not attrs:
            raise serializers.ValidationError('Пустой запрос.')
        return attrs

    def update(self, instance, validated_data):
        """Обновляет аватар пользователя."""
        avatar_data = validated_data.get('avatar', None)
        if avatar_data:
            filename = f'user_{instance.id}_avatar.png'
            instance.avatar.save(filename, avatar_data, save=True)
        return instance

    class Meta:
        model = User
        fields = ['avatar']


class ChangePasswordSerializer(serializers.Serializer):
    """Для смены пароля"""

    current_password = serializers.CharField(write_only=True)
    new_password = serializers.CharField(write_only=True)

    messages = {
        'wrong_password': 'Неправильный текущий пароль.',
        'same_password': 'Новый пароль должен отличаться от текущего.',
    }

    def validate(self, attrs):
        user = self.context.get('user')
        if not user or not isinstance(user, User):
            raise serializers.ValidationError('Ошибка аутентификации.')

        current_password = attrs.get('current_password')
        new_password = attrs.get('new_password')

        if not user.check_password(current_password):
            raise serializers.ValidationError({
                'current_password': self.messages['wrong_password']
            })

        validate_new_password(new_password, current_password)
        return attrs

    def save(self, **kwargs):
        """Обновляет пароль пользователя."""
        user = self.context['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        return user


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'slug')


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit')


class IngredientInRecipeSerializer(serializers.ModelSerializer):
    """Для модели ингредиентов в рецепте."""

    id = serializers.ReadOnlyField(source='ingredient.id')
    name = serializers.ReadOnlyField(source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    """Сериализатор рецепта."""

    tags = TagSerializer(many=True)
    author = UserSerializer()
    ingredients = IngredientInRecipeSerializer(
        source='ingredient_list', many=True)
    is_favorited = serializers.SerializerMethodField()
    is_in_shopping_cart = serializers.SerializerMethodField()

    class Meta:
        model = Recipe
        fields = ('id', 'tags', 'author', 'ingredients',
                  'is_favorited', 'is_in_shopping_cart', 'name',
                  'image', 'text', 'cooking_time'
                  )

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.favorites.filter(user=request.user).exists()

    def get_is_in_shopping_cart(self, obj):
        request = self.context.get('request')
        if request is None or request.user.is_anonymous:
            return False
        return obj.shopping_cart.filter(user=request.user).exists()


class CreateIngredientsInRecipeSerializer(serializers.ModelSerializer):
    """Для ингредиентов в рецептах."""

    id = serializers.IntegerField()
    amount = serializers.IntegerField(
        min_value=MINIMUM,
        max_value=MAXIMUM
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount')


class ShortRecipeSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class CreateRecipeSerializer(serializers.ModelSerializer):
    """Для создания рецептов"""

    ingredients = CreateIngredientsInRecipeSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        many=True, queryset=Tag.objects.all()
    )
    image = Base64ImageField(use_url=True)
    cooking_time = serializers.IntegerField(
        min_value=MINIMUM, max_value=MAXIMUM
    )

    class Meta:
        model = Recipe
        fields = ('ingredients', 'tags', 'name',
                  'image', 'text', 'cooking_time')

    def to_representation(self, instance):
        serializer = RecipeSerializer(
            instance,
            context={
                'request': self.context.get('request')
            }
        )
        return serializer.data

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredient_ids = [ingredient['id'] for ingredient in ingredients]

        if len(ingredient_ids) != len(set(ingredient_ids)):
            raise serializers.ValidationError('Ингредиенты не уникальные!')

        return data

    def create_ingredients(self, ingredients, recipe):
        recipe_ingredients = [
            RecipeIngredient(
                ingredient=Ingredient.objects.get(pk=element['id']),
                recipe=recipe,
                amount=element['amount']
            )
            for element in ingredients
        ]
        RecipeIngredient.objects.bulk_create(recipe_ingredients)

    def create_tags(self, tags, recipe):
        recipe.tags.set(tags)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')

        user = self.context.get('request').user
        recipe = Recipe.objects.create(**validated_data, author=user)
        self.create_ingredients(ingredients, recipe)
        self.create_tags(tags, recipe)
        return recipe

    def update(self, instance, validated_data):
        ingredients = validated_data.pop('ingredients', [])
        tags = validated_data.pop('tags', [])

        if ingredients:
            RecipeIngredient.objects.filter(recipe=instance).delete()
            self.create_ingredients(ingredients, instance)

        if tags:
            instance.tags.set(tags)

        return super().update(instance, validated_data)


class AddFavoritesSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')

    def validate(self, data):
        recipe = self.instance
        request = self.context.get('request')

        if recipe.author == request.user:
            raise serializers.ValidationError(
                f'Нельзя добавить свой "{recipe.name}" в избранное'
            )

        return data


class FollowSerializer(UserReadSerializer):
    recipes = serializers.SerializerMethodField(
        read_only=True,
        method_name='get_recipes')
    recipes_count = serializers.SerializerMethodField(
        read_only=True
    )

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count',)

    def get_recipes(self, obj):
        request = self.context.get('request')
        recipes_limit = request.query_params.get('recipes_limit')
        recipes = obj.recipes.all()
        if recipes_limit:
            try:
                recipes = recipes[:int(recipes_limit)]
            except ValueError:
                pass
        return ShortRecipeSerializer(recipes, many=True).data

    @staticmethod
    def get_recipes_count(obj):
        return obj.recipes.count()
