from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.utils import is_site_admin
from articles.models import Article


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
