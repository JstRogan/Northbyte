from django.contrib import admin

from articles.models import Article, ArticleRating, Bookmark, Category


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "slug")
    prepopulated_fields = {"slug": ("name",)}


@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    list_display = ("title", "author", "category", "status", "created_at")
    list_filter = ("status", "category", "created_at")
    search_fields = ("title", "excerpt", "content", "author__username")
    prepopulated_fields = {"slug": ("title",)}


admin.site.register(ArticleRating)
admin.site.register(Bookmark)
