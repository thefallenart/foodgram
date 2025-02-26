from rest_framework.pagination import PageNumberPagination


class RecipePagination(PageNumberPagination):
    """Кастомная пагинация для рецептов."""
    page_size = 6  # Количество рецептов на одной странице
    page_size_query_param = 'limit'
