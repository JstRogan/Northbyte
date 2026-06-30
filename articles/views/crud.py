from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _

from accounts.utils import is_site_admin
from articles.forms import ArticleForm
from articles.models import Article


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
            messages.success(request, _("Статья сохранена."))
            return redirect("articles:detail", slug=article.slug)
    else:
        form = ArticleForm()
    return render(request, "articles/article_form.html", {"form": form, "mode": "create"})


@login_required
def article_update(request, slug):
    article = get_object_or_404(Article, slug=slug)
    can_manage = is_site_admin(request.user)
    if article.author != request.user and not can_manage:
        return HttpResponseForbidden(_("Редактировать можно только свои статьи."))

    if request.method == "POST":
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            article = form.save(commit=False)
            if not can_manage:
                article.status = Article.Status.PENDING
            article.save()
            messages.success(request, _("Статья обновлена."))
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
        return HttpResponseForbidden(_("Удалять можно только свои статьи."))
    if request.method == "POST":
        article.delete()
        messages.success(request, _("Статья удалена."))
        return redirect("articles:my_articles")
    return render(request, "articles/article_confirm_delete.html", {"article": article})


@login_required
def my_articles(request):
    articles = Article.objects.filter(author=request.user).select_related("category")
    return render(request, "articles/my_articles.html", {"articles": articles})
