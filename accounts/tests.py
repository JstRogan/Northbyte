from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountRoleTests(TestCase):
    def setUp(self):
        self.superadmin = User.objects.create_superuser(
            "root",
            "root@example.com",
            "pass12345",
        )
        self.admin = User.objects.create_user(
            "editor",
            "editor@example.com",
            "pass12345",
            role=User.Role.ADMIN,
        )
        self.user = User.objects.create_user("member", "member@example.com", "pass12345")

    def test_register_creates_regular_user(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "newbie",
                "email": "newbie@example.com",
                "password": "pass12345",
                "confirm_password": "pass12345",
            },
        )

        self.assertRedirects(response, reverse("accounts:dashboard"))
        newbie = User.objects.get(username="newbie")
        self.assertEqual(newbie.role, User.Role.USER)

    def test_register_rejects_taken_username(self):
        response = self.client.post(
            reverse("accounts:register"),
            {
                "username": "member",
                "email": "other@example.com",
                "password": "pass12345",
                "confirm_password": "pass12345",
            },
        )

        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.filter(email="other@example.com").count(), 0)

    def test_banned_user_cannot_login(self):
        self.user.is_banned = True
        self.user.save(update_fields=["is_banned"])

        response = self.client.post(
            reverse("accounts:login"),
            {"username": "member", "password": "pass12345"},
        )

        self.assertEqual(response.status_code, 200)
        self.assertFalse(response.wsgi_request.user.is_authenticated)

    def test_user_management_closed_for_regular_user(self):
        self.client.login(username="member", password="pass12345")

        response = self.client.get(reverse("accounts:user_management"))

        self.assertEqual(response.status_code, 302)

    def test_super_admin_can_promote_user(self):
        self.client.login(username="root", password="pass12345")

        self.client.post(
            reverse("accounts:update_user_status", kwargs={"user_id": self.user.id}),
            {"action": "promote"},
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.ADMIN)

    def test_admin_cannot_promote_user(self):
        self.client.login(username="editor", password="pass12345")

        self.client.post(
            reverse("accounts:update_user_status", kwargs={"user_id": self.user.id}),
            {"action": "promote"},
        )

        self.user.refresh_from_db()
        self.assertEqual(self.user.role, User.Role.USER)

    def test_admin_can_ban_regular_user(self):
        self.client.login(username="editor", password="pass12345")

        self.client.post(
            reverse("accounts:update_user_status", kwargs={"user_id": self.user.id}),
            {"action": "ban"},
        )

        self.user.refresh_from_db()
        self.assertTrue(self.user.is_banned)
