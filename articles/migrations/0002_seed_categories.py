from django.db import migrations

CATEGORIES = [
    ("Backend", "backend"),
    ("Frontend", "frontend"),
    ("AI", "ai"),
    ("Cyber Security", "cyber-security"),
    ("Cyber Sport", "cyber-sport"),
    ("Game Development", "game-development"),
]


def seed_categories(apps, schema_editor):
    Category = apps.get_model("articles", "Category")
    for name, slug in CATEGORIES:
        Category.objects.get_or_create(slug=slug, defaults={"name": name})


def remove_categories(apps, schema_editor):
    Category = apps.get_model("articles", "Category")
    Category.objects.filter(slug__in=[slug for _, slug in CATEGORIES]).delete()


class Migration(migrations.Migration):

    dependencies = [
        ("articles", "0001_initial"),
    ]

    operations = [
        migrations.RunPython(seed_categories, remove_categories),
    ]
