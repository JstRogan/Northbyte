from django.contrib.auth import get_user_model, login, logout
from django.shortcuts import redirect, render
from django.views.decorators.http import require_POST

from accounts.forms import LoginForm, RegisterForm

User = get_user_model()


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
