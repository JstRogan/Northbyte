from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        SUPERADMIN = "superadmin", "Супер Админ"
        ADMIN = "admin", "Админ"
        USER = "user", "Пользователь"

    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.USER,
    )
    avatar = models.ImageField(upload_to="avatars/", null=True, blank=True)
    bio = models.TextField(max_length=500, blank=True)
    is_banned = models.BooleanField(default=False)

    def is_site_admin(self):
        return self.is_superuser or self.role in [self.Role.ADMIN, self.Role.SUPERADMIN]

    def __str__(self):
        return self.username
