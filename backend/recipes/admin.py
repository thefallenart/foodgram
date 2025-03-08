from django.contrib import admin
from recipes import models


@admin.register(models.Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit')
    list_filter = ('name',)
    search_fields = ('name',)
    empty_value_display = '-отсутствует-'


@admin.register(models.Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'slug')
    list_editable = ('name', 'slug')
    search_fields = ('name', 'slug')
    empty_value_display = '-отсутствует-'


@admin.register(models.Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'author', 'get_favorites_count',
                    'cooking_time', 'text', 'get_tags', 'image')
    list_editable = ('name', 'cooking_time', 'text', 'image', 'author')
    readonly_fields = ('get_favorites_count',)
    list_filter = ('name', 'author', 'tags')
    search_fields = ('name', 'author__username', 'tags__name')
    empty_value_display = '-отсутствует-'

    @admin.display(description='В избранном')
    def get_favorites_count(self, obj):
        return obj.favorites.count()

    @admin.display(description='Теги')
    def get_tags(self, obj):
        return ", ".join(tag.name for tag in obj.tags.all())


@admin.register(models.RecipeIngredient)
class RecipeIngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_recipe_name', 'get_ingredient_name', 'amount')
    list_editable = ('amount',)
    search_fields = ('recipe__name', 'ingredient__name')
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-отсутствует-'

    @admin.display(description='Рецепт')
    def get_recipe_name(self, obj):
        return obj.recipe.name

    @admin.display(description='Ингредиент')
    def get_ingredient_name(self, obj):
        return obj.ingredient.name


@admin.register(models.Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_username', 'get_recipe_name',
                    'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    empty_value_display = '-отсутствует-'

    @admin.display(description='Пользователь')
    def get_user_username(self, obj):
        return obj.user.username

    @admin.display(description='Рецепт')
    def get_recipe_name(self, obj):
        return obj.recipe.name


@admin.register(models.ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'get_user_username', 'get_recipe_name',
                    'user', 'recipe')
    list_editable = ('user', 'recipe')
    search_fields = ('user__username', 'recipe__name')
    list_filter = ('user', 'recipe')
    empty_value_display = '-отсутствует-'

    @admin.display(description='Пользователь')
    def get_user_username(self, obj):
        return obj.user.username

    @admin.display(description='Рецепт')
    def get_recipe_name(self, obj):
        return obj.recipe.name
