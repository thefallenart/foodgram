from django.db.models import Prefetch, Sum
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect
from django_filters.rest_framework import DjangoFilterBackend
from hashids import Hashids
from recipes.models import (Favorite, Follow, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Tag)
from rest_framework import mixins, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet
from users.models import User

from .filters import IngredientFilter, RecipeFilter
from .pagination import RecipePagination
from .premissions import IsAuthorOrReadOnly
from .serializers import (AddFavoritesSerializer, AvatarSerializer,
                          ChangePasswordSerializer, CreateRecipeSerializer,
                          FollowSerializer, IngredientSerializer,
                          RecipeSerializer, TagSerializer,
                          UserCustomCreateSerializer, UserReadSerializer)


class UserViewSet(mixins.CreateModelMixin,
                  mixins.ListModelMixin,
                  mixins.RetrieveModelMixin,
                  viewsets.GenericViewSet):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    pagination_class = RecipePagination

    def get_serializer_class(self):
        if self.action in ('list', 'retrieve'):
            return UserReadSerializer
        return UserCustomCreateSerializer

    @action(detail=False, methods=['get'],
            pagination_class=None,
            permission_classes=(IsAuthenticated,))
    def me(self, request):
        serializer = UserReadSerializer(request.user)
        return Response(serializer.data,
                        status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'],
            permission_classes=(IsAuthenticated,))
    def set_password(self, request):
        """Обновление пароля текущего пользователя."""
        serializer = ChangePasswordSerializer(
            data=request.data, context={"user": request.user}
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return Response({'detail': 'Пароль успешно изменен!'},
                        status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated, ),
        url_path='subscriptions',
        url_name='subscriptions',
    )
    def subscriptions(self, request):
        """Метод для создания страницы подписок"""

        queryset = User.objects.filter(following__user=self.request.user)
        if queryset:
            pages = self.paginate_queryset(queryset)
            serializer = FollowSerializer(pages, many=True,
                                          context={'request': request})
            return self.get_paginated_response(serializer.data)
        return Response('Вы ни на кого не подписаны.',
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,),
        url_path='subscribe',
        url_name='subscribe',
    )
    def subscribe(self, request, pk):

        user = request.user
        author = get_object_or_404(User, id=pk)

        if user == author:
            return Response({'errors': 'Нельзя подписаться на себя!'},
                            status=status.HTTP_400_BAD_REQUEST)

        subscription = Follow.objects.filter(user=user, author=author)

        if request.method == 'POST':
            if subscription.exists():
                return Response({'errors': 'Вы уже подписаны!'},
                                status=status.HTTP_400_BAD_REQUEST)
            Follow.objects.create(user=user, author=author)
            serializer = FollowSerializer(author, context={'request': request})
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if subscription.exists():
            subscription.delete()
            return Response({'message': 'Вы отписались'},
                            status=status.HTTP_204_NO_CONTENT)

        return Response({'errors': 'Вы не подписаны на этого пользователя'},
                        status=status.HTTP_400_BAD_REQUEST)

    @action(
        detail=False,
        methods=['put'],
        permission_classes=[IsAuthenticated],
        url_path='me/avatar'
    )
    def avatar(self, request, *args, **kwargs):
        user = self.request.user
        if user.avatar:
            user.avatar.delete()

        serializer = AvatarSerializer(instance=user, data=request.data)
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response({"avatar": user.avatar.url}, status=status.HTTP_200_OK)

    @avatar.mapping.delete
    def delete_avatar(self, request):
        """Удаление аватара пользователя"""
        user = request.user

        if user.avatar:
            user.avatar.delete(save=False)
            user.avatar = None
            user.save()
            return Response(status=status.HTTP_204_NO_CONTENT)

        return Response(
            {'detail': 'Аватар не найден.'},
            status=status.HTTP_404_NOT_FOUND
        )


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет работы с обьектами класса Tag."""

    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    permission_classes = (AllowAny,)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """Вьюсет для работы с обьектами класса Ingredient."""

    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = (AllowAny,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = IngredientFilter
    pagination_class = None
    search_fields = ('^name',)


class RecipeViewSet(ModelViewSet):
    """ViewSet для обработки запросов, связанных с рецептами."""

    queryset = Recipe.objects.prefetch_related('ingredient_list').all()
    pagination_class = RecipePagination
    permission_classes = (IsAuthorOrReadOnly,)
    filter_backends = (DjangoFilterBackend,)
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        """Метод для вызова определенного сериализатора."""
        if self.action in ('list', 'retrieve'):
            return RecipeSerializer
        elif self.action in ('create', 'partial_update'):
            return CreateRecipeSerializer

    def get_serializer_context(self):
        """Метод для передачи контекста."""
        context = super().get_serializer_context()
        context.update({'request': self.request})
        return context

    def get_queryset(self):
        """Оптимизация запросов с предзагрузкой избранного и корзины."""
        user = self.request.user
        queryset = Recipe.objects.all()
        if user.is_authenticated:
            queryset = queryset.prefetch_related(
                Prefetch(
                    'favorites',
                    queryset=Favorite.objects.filter(user=user)
                ),
                Prefetch(
                    'shopping_cart',
                    queryset=ShoppingCart.objects.filter(user=user)
                )
            )

    def _handle_action(self, request, model, serializer_class, error_msg, pk):
        """Общий метод для добавления/удаления объектов."""
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)

        if request.method == 'POST':
            if model.objects.filter(user=user, recipe=recipe).exists():
                return Response(
                    {'errors': error_msg.format(recipe.name)},
                    status=status.HTTP_400_BAD_REQUEST
                )
            model.objects.create(user=user, recipe=recipe)
            serializer = serializer_class(recipe)
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        if request.method == 'DELETE':
            obj = model.objects.filter(user=user, recipe=recipe)
            if obj.exists():
                obj.delete()
                return Response(status=status.HTTP_204_NO_CONTENT)
            return Response(
                {'errors': f'Рецепт "{recipe.name}" не найден в списке.'},
                status=status.HTTP_400_BAD_REQUEST
            )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        """Добавление/удаление рецепта из избранного."""
        return self._handle_action(
            request, Favorite, AddFavoritesSerializer,
            'Рецепт "{}" уже есть в избранном.', pk
        )

    @action(
        detail=True,
        methods=('post', 'delete'),
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        """Добавление/удаление рецепта из списка покупок."""
        return self._handle_action(
            request, ShoppingCart, AddFavoritesSerializer,
            'Рецепт "{}" уже есть в списке покупок.', pk
        )

    @staticmethod
    def ingredients_to_txt(ingredients):
        """Формирование текстового списка ингредиентов."""
        return '\n'.join(
            f"{ingredient['ingredient__name']} - {ingredient['sum']} "
            f"({ingredient['ingredient__measurement_unit']})"
            for ingredient in ingredients
        )

    @action(
        detail=False,
        methods=('get',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request):
        """Загрузка списка покупок в текстовом формате."""
        ingredients = RecipeIngredient.objects.filter(
            recipe__shopping_cart__user=request.user
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(sum=Sum('amount'))

        shopping_list = self.ingredients_to_txt(ingredients)
        return HttpResponse(shopping_list, content_type='text/plain')

    @action(detail=True, methods=['get'], url_path='get-link')
    def get_link(self, request, pk=None):
        """Генерирует короткую ссылку на рецепт."""
        recipe = self.get_object()

        hashids = Hashids(salt="foodgramacheron", min_length=5)
        short_code = hashids.encode(recipe.id)

        short_link = f"https://foodgramacheron.zapto.org/s/{short_code}"
        return Response({"short-link": short_link}, status=status.HTTP_200_OK)


def short_link_redirect(request, short_code):
    """Перенаправляет пользователя на страницу рецепта по короткой ссылке."""
    hashids = Hashids(salt="foodgramacheron", min_length=5)
    recipe_id = hashids.decode(short_code)
    if not recipe_id:
        return redirect('/')
    recipe = get_object_or_404(Recipe, id=recipe_id[0])
    return redirect(f'/recipes/{recipe.pk}/')
