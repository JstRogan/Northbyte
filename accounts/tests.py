from django.contrib.auth.models import Group, User
from django.test import TestCase
from django.urls import reverse


class AccountRoleTests(TestCase):
    def setUp(self):
        self.superuser = User.objects.create_superuser(
            "root",
            "root@example.com",
            "pass12345",
        )
        self.admin = User.objects.create_user(
            "editor",
            "editor@example.com",
            "pass12345",
            is_staff=True,
        )
        self.admin_group = Group.objects.get(name="news_admin")
        self.admin.groups.add(self.admin_group)
        self.user = User.objects.create_user("member", "member@example.com", "pass12345")

    def test_super_admin_can_promote_user(self):
        self.client.login(username="root", password="pass12345")

        self.client.post(
            reverse("accounts:update_user_status", kwargs={"user_id": self.user.id}),
            {"action": "promote"},
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_staff)
        self.assertTrue(self.user.groups.filter(name="news_admin").exists())

    def test_admin_can_ban_regular_user(self):
        self.client.login(username="editor", password="pass12345")

        self.client.post(
            reverse("accounts:update_user_status", kwargs={"user_id": self.user.id}),
            {"action": "ban"},
        )

        self.user.refresh_from_db()
        self.assertFalse(self.user.is_active)
