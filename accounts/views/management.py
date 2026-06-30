from django.contrib import messages
from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import get_object_or_404, redirect, render
from django.utils.translation import gettext as _
from django.views.decorators.http import require_POST

from accounts.utils import is_site_admin

User = get_user_model()


@login_required
@user_passes_test(is_site_admin)
def user_management(request):
    users = User.objects.order_by("username")
    return render(request, "accounts/user_management.html", {"users": users})


@login_required
@require_POST
@user_passes_test(is_site_admin)
def update_user_status(request, user_id):
    target = get_object_or_404(User, pk=user_id)
    action = request.POST.get("action")

    if target.is_superuser and not request.user.is_superuser:
        messages.error(request, _("Управлять супер админом может только супер админ."))
        return redirect("accounts:user_management")

    if action == "ban" and target != request.user:
        target.is_banned = True
        target.save(update_fields=["is_banned"])
    elif action == "unban":
        target.is_banned = False
        target.save(update_fields=["is_banned"])
    elif action == "promote" and request.user.is_superuser:
        target.role = User.Role.ADMIN
        target.save(update_fields=["role"])
    elif action == "demote" and request.user.is_superuser and not target.is_superuser:
        target.role = User.Role.USER
        target.save(update_fields=["role"])
    else:
        messages.error(request, _("Действие недоступно."))

    return redirect("accounts:user_management")
