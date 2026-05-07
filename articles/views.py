from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.core.paginator import Paginator
from django.db.models import Avg
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.utils import is_site_admin
from articles.forms import ArticleForm
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
        {"page_obj": page_obj, "page_title": "Popular"},
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
        return HttpResponseForbidden("This article is waiting for moderation.")

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


@login_required
def article_create(request):
    if request.method == "POST":
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            if is_site_admin(request.user):
                article.publish()
            else:
                article.status = Article.Status.PENDING
            article.save()
            messages.success(request, "Article saved.")
            return redirect("articles:detail", slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, "articles/article_form.html", {"form": form, "mode": "create"})


@login_required
def article_update(request, slug):
    article = get_object_or_404(Article, slug=slug)
    can_manage = is_site_admin(request.user)
    if article.author != request.user and not can_manage:
        return HttpResponseForbidden("You can edit only your own articles.")

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if not can_manage:
                article.status = Article.Status.PENDING
            article.save()
            messages.success(request, "Article updated.")
            return redirect("articles:detail", slug=article.slug)
    else:
        form = ArticleForm(instance=article)
    return render(
        request,
        "articles/article_form.html",
        {"form": form, "mode": "edit", "article": article},
    )


@login_required
def article_delete(request, slug):
    article = get_object_or_404(Article, slug=slug)
    if article.author != request.user and not is_site_admin(request.user):
        return HttpResponseForbidden("You can delete only your own articles.")
    if request.method == "POST":
        article.delete()
        messages.success(request, "Article deleted.")
        return redirect("articles:my_articles")
    return render(request, "articles/article_confirm_delete.html", {"article": article})


@login_required
def my_articles(request):
    articles = Article.objects.filter(author=request.user).select_related("category")
    return render(request, "articles/my_articles.html", {"articles": articles})


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
        messages.error(request, "Rating must be from 1 to 5.")
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


@login_required
@user_passes_test(is_site_admin)
def moderation_queue(request):
    articles = Article.objects.exclude(status=Article.Status.PUBLISHED).select_related(
        "author",
        "category",
    )
    return render(request, "articles/moderation_queue.html", {"articles": articles})


@login_required
@require_POST
@user_passes_test(is_site_admin)
def moderate_article(request, slug):
    article = get_object_or_404(Article, slug=slug)
    action = request.POST.get("action")
    if action == "approve":
        article.publish()
        article.save(update_fields=["status", "published_at", "updated_at"])
    elif action == "reject":
        article.status = Article.Status.REJECTED
        article.save(update_fields=["status", "updated_at"])
    return redirect("articles:moderation_queue")
