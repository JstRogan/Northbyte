from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from articles.models import Article, ArticleRating, Bookmark


@login_required
def bookmarks(request):
    saved = (
        Bookmark.objects.filter(user=request.user, article__status=Article.Status.PUBLISHED)
        .select_related("article", "article__author", "article__category")
    )
    return render(request, "articles/bookmarks.html", {"bookmarks": saved})


@login_required
@require_POST
def rate_article(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)
    try:
        score = int(request.POST.get("score", "0"))
    except ValueError:
        score = 0
    if score not in range(1, 6):
        messages.error(request, _("Оценка должна быть от 1 до 5."))
        return redirect("articles:detail", slug=article.slug)
    ArticleRating.objects.update_or_create(
        article=article,
        user=request.user,
        defaults={"score": score},
    )
    return redirect("articles:detail", slug=article.slug)


@login_required
@require_POST
def toggle_bookmark(request, slug):
    article = get_object_or_404(Article, slug=slug, status=Article.Status.PUBLISHED)
    bookmark, created = Bookmark.objects.get_or_create(article=article, user=request.user)
    if not created:
        bookmark.delete()
    return redirect("articles:detail", slug=article.slug)
