from datetime import timedelta

from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand
from django.utils import timezone

from articles.management.commands._demo_data import ARTICLES, AUTHORS, IMG
from articles.models import Article, ArticleRating, Bookmark, Category

User = get_user_model()
DEMO_PASSWORD = "northbyte-demo"


class Command(BaseCommand):
    help = "Wipe articles and load a coherent demo dataset with thematic images."

    def handle(self, *args, **options):
        Bookmark.objects.all().delete()
        ArticleRating.objects.all().delete()
        Article.objects.all().delete()

        authors = {}
        for data in AUTHORS:
            user, _ = User.objects.get_or_create(username=data["username"])
            user.role = data["role"]
            user.bio = data["bio"]
            user.set_password(DEMO_PASSWORD)
            user.save()
            authors[data["username"]] = user

        raters = list(User.objects.all())
        now = timezone.now()

        for index, item in enumerate(ARTICLES):
            title, category_slug, author_key, image_id, status, ratings, excerpt, content = item
            article = Article(
                title=title,
                author=authors[author_key],
                category=Category.objects.get(slug=category_slug),
                image_url=IMG.format(image_id),
                excerpt=excerpt,
                content=content,
                status=status,
            )
            if status == Article.Status.PUBLISHED:
                article.published_at = now - timedelta(days=index)
            article.save()
            Article.objects.filter(pk=article.pk).update(
                created_at=now - timedelta(days=index, hours=index)
            )

            pool = [user for user in raters if user != article.author]
            for score, rater in zip(ratings, pool):
                ArticleRating.objects.create(article=article, user=rater, score=score)

        reader = User.objects.exclude(username__in=[a["username"] for a in AUTHORS]).first()
        if reader:
            for article in Article.objects.filter(status=Article.Status.PUBLISHED)[:4]:
                Bookmark.objects.get_or_create(article=article, user=reader)

        self.stdout.write(
            self.style.SUCCESS(
                f"Seeded {len(ARTICLES)} articles and {len(authors)} demo authors "
                f"(demo password: {DEMO_PASSWORD})."
            )
        )
