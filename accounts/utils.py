def is_site_admin(user):
    return bool(user.is_authenticated and user.is_site_admin())
