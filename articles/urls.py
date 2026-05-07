from django.urls import path

from articles import views

app_name = "articles"

urlpatterns = [
    path("", views.article_list, name="list"),
    path("articles/", views.article_list, name="article_list"),
    path("articles/popular/", views.popular_articles, name="popular"),
    path("articles/create/", views.article_create, name="create"),
    path("articles/mine/", views.my_articles, name="my_articles"),
    path("articles/bookmarks/", views.bookmarks, name="bookmarks"),
    path("articles/moderation/", views.moderation_queue, name="moderation_queue"),
    path("articles/<slug:slug>/", views.article_detail, name="detail"),
    path("articles/<slug:slug>/edit/", views.article_update, name="update"),
    path("articles/<slug:slug>/delete/", views.article_delete, name="delete"),
    path("articles/<slug:slug>/rate/", views.rate_article, name="rate"),
    path("articles/<slug:slug>/bookmark/", views.toggle_bookmark, name="toggle_bookmark"),
    path("articles/<slug:slug>/moderate/", views.moderate_article, name="moderate"),
    path("categories/", views.category_list, name="categories"),
    path("categories/<slug:slug>/", views.category_detail, name="category_detail"),
]
