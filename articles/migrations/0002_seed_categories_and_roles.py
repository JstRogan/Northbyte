from django.db import migrations


def seed_categories_and_roles(apps, schema_editor):
    Category = apps.get_model("articles", "Category")
    Group = apps.get_model("auth", "Group")
    categories = [
        ("Backend", "backend"),
        ("Frontend", "frontend"),
        ("AI", "ai"),
        ("Cyber Security", "cyber-security"),
        ("Cyber Sport", "cyber-sport"),
        ("Game Development", "game-development"),
    ]
    for name, slug in categories:
        Category.objects.get_or_create(slug=slug, defaults={"name": name})
    Group.objects.get_or_create(name="news_admin")


class Migration(migrations.Migration):
    dependencies = [
        ("articles", "0001_initial"),
        ("auth", "0012_alter_user_first_name_max_length"),
    ]

    operations = [
        migrations.RunPython(seed_categories_and_roles, migrations.RunPython.noop),
    ]
