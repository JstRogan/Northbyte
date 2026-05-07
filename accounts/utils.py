NEWS_ADMIN_GROUP = "news_admin"


def is_news_admin(user):
    return bool(
        user.is_authenticated
        and user.is_staff
        and user.groups.filter(name=NEWS_ADMIN_GROUP).exists()
    )


def is_site_admin(user):
    return bool(user.is_authenticated and (user.is_superuser or is_news_admin(user)))
