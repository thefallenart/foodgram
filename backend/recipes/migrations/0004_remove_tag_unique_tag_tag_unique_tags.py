# Generated by Django 4.2.19 on 2025-02-26 00:18

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0003_remove_recipeingredient_unique_recipe_ingredient_and_more'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='tag',
            name='unique_tag',
        ),
        migrations.AddConstraint(
            model_name='tag',
            constraint=models.UniqueConstraint(fields=('name', 'slug'), name='unique_tags'),
        ),
    ]
