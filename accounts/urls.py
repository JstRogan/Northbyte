from django.urls import path

from accounts import views

app_name = "accounts"

urlpatterns = [
    path("register/", views.register_view, name="register"),
    path("login/", views.login_view, name="login"),
    path("logout/", views.logout_view, name="logout"),
    path("dashboard/", views.dashboard_view, name="dashboard"),
    path("authors/", views.authors_list, name="authors_list"),
    path("authors/<str:username>/", views.author_detail, name="author_detail"),
    path("users/", views.user_management, name="user_management"),
    path("users/<int:user_id>/", views.update_user_status, name="update_user_status"),
]
