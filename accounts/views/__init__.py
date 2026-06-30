from accounts.views.auth import login_view, logout_view, register_view
from accounts.views.profile import author_detail, authors_list, dashboard_view
from accounts.views.management import update_user_status, user_management

__all__ = [
    "register_view",
    "login_view",
    "logout_view",
    "dashboard_view",
    "authors_list",
    "author_detail",
    "user_management",
    "update_user_status",
]
