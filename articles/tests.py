from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse

from articles.models import Article, ArticleRating, Bookmark, Category


IMAGE_URL = "https://res.cloudinary.com/demo/image/upload/sample.jpg"


class ArticleWorkflowTests(TestCase):
    def setUp(self):
        self.category = Category.objects.get(slug="backend")
        self.user = User.objects.create_user("writer", "writer@example.com", "pass12345")
        self.reader = User.objects.create_user("reader", "reader@example.com", "pass12345")
        self.admin = User.objects.create_user(
            "editor",
            "editor@example.com",
            "pass12345",
            is_staff=True,
        )
        self.admin.groups.add(Group.objects.get(name="news_admin"))

    def make_article(self, author=None, status=Article.Status.PUBLISHED, title="Django news"):
        article = Article(
            title=title,
            author=author or self.user,
            image_url=IMAGE_URL,
            excerpt="Short useful preview",
            content="Full article content",
            category=self.category,
            status=status,
        )
        if status == Article.Status.PUBLISHED:
            article.publish()
        article.save()
        return article

    def test_guest_can_read_published_article(self):
        article = self.make_article()

        response = self.client.get(reverse("articles:detail", kwargs={"slug": article.slug}))

        self.assertEqual(response.status_code, 200)
        self.assertContains(response, article.title)

    def test_regular_user_article_waits_for_moderation(self):
        self.client.login(username="writer", password="pass12345")

        response = self.client.post(
            reverse("articles:create"),
            {
                "title": "Pending story",
                "image_url": IMAGE_URL,
                "excerpt": "Preview",
                "content": "Article body",
                "category": self.category.id,
            },
        )

        article = Article.objects.get(title="Pending story")
        self.assertRedirects(response, reverse("articles:detail", kwargs={"slug": article.slug}))
        self.assertEqual(article.status, Article.Status.PENDING)
        self.client.logout()
        hidden_response = self.client.get(reverse("articles:detail", kwargs={"slug": article.slug}))
        self.assertEqual(hidden_response.status_code, 403)

    def test_admin_can_approve_article(self):
        article = self.make_article(status=Article.Status.PENDING)
        self.client.login(username="editor", password="pass12345")

        self.client.post(
            reverse("articles:moderate", kwargs={"slug": article.slug}),
            {"action": "approve"},
        )

        article.refresh_from_db()
        self.assertEqual(article.status, Article.Status.PUBLISHED)
        self.assertIsNotNone(article.published_at)

    def test_popular_page_requires_average_rating_four_or_more(self):
        popular = self.make_article(title="Popular")
        quiet = self.make_article(title="Quiet")
        ArticleRating.objects.create(article=popular, user=self.reader, score=5)
        ArticleRating.objects.create(article=quiet, user=self.reader, score=3)

        response = self.client.get(reverse("articles:popular"))

        self.assertContains(response, "Popular")
        self.assertNotContains(response, "Quiet")

    def test_bookmark_and_rating_are_unique_per_user(self):
        article = self.make_article()
        self.client.login(username="reader", password="pass12345")

        self.client.post(reverse("articles:rate", kwargs={"slug": article.slug}), {"score": "4"})
        self.client.post(reverse("articles:rate", kwargs={"slug": article.slug}), {"score": "5"})
        self.client.post(reverse("articles:toggle_bookmark", kwargs={"slug": article.slug}))
        self.client.post(reverse("articles:toggle_bookmark", kwargs={"slug": article.slug}))

        self.assertEqual(ArticleRating.objects.count(), 1)
        self.assertEqual(ArticleRating.objects.get().score, 5)
        self.assertEqual(Bookmark.objects.count(), 0)

    def test_user_cannot_edit_another_user_article(self):
        article = self.make_article()
        self.client.login(username="reader", password="pass12345")

        response = self.client.get(reverse("articles:update", kwargs={"slug": article.slug}))

        self.assertEqual(response.status_code, 403)
