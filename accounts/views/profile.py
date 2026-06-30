from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.shortcuts import get_object_or_404, render

from articles.models import Article

User = get_user_model()


@login_required
def dashboard_view(request):
    articles = Article.objects.filter(author=request.user).select_related("category")
    return render(request, "accounts/dashboard.html", {"articles": articles})


def authors_list(request):
    authors = (
        User.objects.filter(articles__status=Article.Status.PUBLISHED, is_banned=False)
        .distinct()
        .order_by("username")
    )
    return render(request, "accounts/authors_list.html", {"authors": authors})


def author_detail(request, username):
    author = get_object_or_404(User, username=username, is_banned=False)
    articles = Article.objects.filter(
        author=author,
        status=Article.Status.PUBLISHED,
    ).select_related("category")
    return render(
        request,
        "accounts/author_detail.html",
        {"profile_user": author, "articles": articles},
    )
