from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.auth.models import Group, User
from django.shortcuts import get_object_or_404, redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import LoginForm, RegisterForm
from accounts.utils import NEWS_ADMIN_GROUP, is_site_admin
from articles.models import Article


def register_view(request):
    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = User.objects.create_user(
                username=form.cleaned_data["username"],
                email=form.cleaned_data["email"],
                password=form.cleaned_data["password"],
            )
            login(request, user)
            return redirect("accounts:dashboard")
    else:
        form = RegisterForm()
    return render(request, "accounts/register.html", {"form": form})


def login_view(request):
    if request.method == "POST":
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            login(request, form.get_user())
            return redirect("accounts:dashboard")
    else:
        form = LoginForm(request)
    return render(request, "accounts/login.html", {"form": form})


@require_POST
def logout_view(request):
    logout(request)
    return redirect("articles:list")


@login_required
def dashboard_view(request):
    articles = Article.objects.filter(author=request.user).select_related("category")
    return render(request, "accounts/dashboard.html", {"articles": articles})


def authors_list(request):
    authors = (
        User.objects.filter(articles__status=Article.Status.PUBLISHED, is_active=True)
        .distinct()
        .order_by("username")
    )
    return render(request, "accounts/authors_list.html", {"authors": authors})


def author_detail(request, username):
    author = get_object_or_404(User, username=username, is_active=True)
    articles = Article.objects.filter(
        author=author,
        status=Article.Status.PUBLISHED,
    ).select_related("category")
    return render(
        request,
        "accounts/author_detail.html",
        {"profile_user": author, "articles": articles},
    )


@login_required
@user_passes_test(is_site_admin)
def user_management(request):
    users = User.objects.order_by("username").prefetch_related("groups")
    admin_group, _ = Group.objects.get_or_create(name=NEWS_ADMIN_GROUP)
    return render(
        request,
        "accounts/user_management.html",
        {"users": users, "admin_group": admin_group},
    )


@login_required
@require_POST
@user_passes_test(is_site_admin)
def update_user_status(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    action = request.POST.get("action")
    admin_group, _ = Group.objects.get_or_create(name=NEWS_ADMIN_GROUP)

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, "Only a super admin can manage another super admin.")
        return redirect("accounts:user_management")

    if action == "ban" and target != request.user:
        target.is_active = False
        target.save(update_fields=["is_active"])
    elif action == "unban":
        target.is_active = True
        target.save(update_fields=["is_active"])
    elif action == "promote" and request.user.is_superuser:
        target.is_staff = True
        target.groups.add(admin_group)
        target.save(update_fields=["is_staff"])
    elif action == "demote" and request.user.is_superuser and not target.is_superuser:
        target.groups.remove(admin_group)
        target.is_staff = False
        target.save(update_fields=["is_staff"])
    else:
        messages.error(request, "Action is not allowed.")

    return redirect("accounts:user_management")
