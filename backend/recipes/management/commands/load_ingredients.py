import csv
import os

from django.core.management.base import BaseCommand

from foodgram import settings
from recipes.models import Ingredient


def ingredient_create(row):
    """Создание ингредиента, если его нет в базе."""
    Ingredient.objects.get_or_create(
        name=row[0],
        measurement_unit=row[1]
    )


class Command(BaseCommand):
    help = "Load ingredients to DB"

    def handle(self, *args, **options):
        path = os.path.join(settings.BASE_DIR, 'ingredients.csv')

        with open(path, 'r', encoding='utf-8') as file:
            reader = csv.reader(file)
            next(reader)
            for row in reader:
                ingredient_create(row)

        self.stdout.write(self.style.SUCCESS("Выполнено!"))
