from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, render
from django.utils.translation import gettext as _

from accounts.utils import is_site_admin
from articles.models import Article, ArticleRating, Bookmark, Category


def published_articles():
    return (
        Article.objects.filter(status=Article.Status.PUBLISHED)
        .select_related("author", "category")
        .order_by("-created_at")
    )


def paginate(request, queryset, per_page=6):
    paginator = Paginator(queryset, per_page)
    return paginator.get_page(request.GET.get("page"))


def article_list(request):
    page_obj = paginate(request, published_articles())
    return render(request, "articles/article_list.html", {"page_obj": page_obj})


def popular_articles(request):
    articles = (
        published_articles()
        .annotate(avg_score=Avg("ratings__score"))
        .filter(avg_score__gte=4)
    )
    page_obj = paginate(request, articles)
    return render(
        request,
        "articles/article_list.html",
        {"page_obj": page_obj, "page_title": _("Популярное")},
    )


def category_list(request):
    categories = Category.objects.order_by("name")
    return render(request, "articles/category_list.html", {"categories": categories})


def category_detail(request, slug):
    category = get_object_or_404(Category, slug=slug)
    page_obj = paginate(request, published_articles().filter(category=category))
    return render(
        request,
        "articles/article_list.html",
        {"page_obj": page_obj, "page_title": category.name, "category": category},
    )


def article_detail(request, slug):
    article = get_object_or_404(
        Article.objects.select_related("author", "category"),
        slug=slug,
    )
    can_manage = is_site_admin(request.user)
    if article.status != Article.Status.PUBLISHED and article.author != request.user and not can_manage:
        return HttpResponseForbidden(_("Эта статья ожидает модерации."))

    user_rating = None
    is_bookmarked = False
    if request.user.is_authenticated:
        user_rating = ArticleRating.objects.filter(article=article, user=request.user).first()
        is_bookmarked = Bookmark.objects.filter(article=article, user=request.user).exists()

    return render(
        request,
        "articles/article_detail.html",
        {
            "article": article,
            "user_rating": user_rating,
            "is_bookmarked": is_bookmarked,
            "can_manage": can_manage,
        },
    )
