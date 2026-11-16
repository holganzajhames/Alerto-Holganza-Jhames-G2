from django.test import Client, TestCase
from django.urls import reverse

from .models import User


class AccountFlowTests(TestCase):
    password = "Campus!demo-54-willow"

    def setUp(self):
        self.registration = {
            "username": "student",
            "email": "student@example.com",
            "password1": self.password,
            "password2": self.password,
        }

    def make_user(self, username="student"):
        return User.objects.create_user(username, f"{username}@example.com", self.password)

    def test_register_then_login_and_logout(self):
        response = self.client.post(reverse("register"), self.registration, follow=True)
        self.assertContains(response, "Account created.")
        user = User.objects.get(username="student")
        self.assertFalse(user.is_staff)
        self.assertNotEqual(user.password, self.password)
        self.assertTrue(user.check_password(self.password))

        response = self.client.post(reverse("login"), {
            "username": user.username,
            "password": self.password,
        }, follow=True)
        self.assertContains(response, "Student dashboard")
        self.assertEqual(self.client.get(reverse("logout")).status_code, 405)
        response = self.client.post(reverse("logout"), follow=True)
        self.assertContains(response, "You have been signed out.")
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_registration_validation(self):
        self.make_user()
        invalid_cases = [
            ({"username": ""}, "username"),
            ({"email": ""}, "email"),
            ({"email": "wrong"}, "email"),
            ({"password2": "mismatch"}, "password2"),
            ({"email": "other@example.com", "username": "STUDENT"}, "username"),
        ]
        for changed_fields, field in invalid_cases:
            with self.subTest(changed_fields=changed_fields):
                response = self.client.post(reverse("register"), {
                    **self.registration, "username": "other", "email": "other@example.com",
                    **changed_fields,
                })
                self.assertTrue(response.context["form"].errors[field])

        response = self.client.post(reverse("register"), {
            **self.registration, "username": "other", "email": "STUDENT@example.com",
        })
        self.assertTrue(response.context["form"].errors)
        self.assertEqual(User.objects.count(), 1)

    def test_invalid_login_shows_error(self):
        self.make_user()
        response = self.client.post(reverse("login"), {"username": "student", "password": "wrong"})
        self.assertTrue(response.context["form"].non_field_errors())
        self.assertNotIn("_auth_user_id", self.client.session)

    def test_logged_out_users_are_redirected_from_protected_pages(self):
        for route in ("dashboard", "admin_dashboard", "student_dashboard", "profile", "edit_profile"):
            url = reverse(route)
            self.assertRedirects(self.client.get(url), f"{reverse('login')}?next={url}")

    def test_other_role_dashboard_is_forbidden(self):
        self.client.force_login(self.make_user())
        self.assertEqual(self.client.get(reverse("admin_dashboard")).status_code, 403)
        User.objects.create_superuser("admin", "admin@example.com", self.password)
        response = self.client.post(reverse("login"), {}, follow=True)
        self.assertContains(response, "Student dashboard")
        self.client.logout()
        response = self.client.post(reverse("login"), {
            "username": "admin", "password": self.password,
        }, follow=True)
        self.assertContains(response, "Administrator dashboard")
        self.assertEqual(self.client.get(reverse("student_dashboard")).status_code, 403)

    def test_profile_is_scoped_to_signed_in_user(self):
        user = self.make_user()
        other = self.make_user("other")
        self.client.force_login(user)
        response = self.client.get(reverse("profile"), {"id": other.pk})
        self.assertContains(response, user.email)
        self.assertNotContains(response, other.email)

        response = self.client.post(reverse("edit_profile"), {
            "id": other.pk,
            "is_staff": "on",
            "first_name": "Sam",
            "last_name": "Reyes",
            "email": "new@example.com",
            "contact_number": "+63 912 345 6789",
        }, follow=True)
        self.assertContains(response, "Profile updated.")
        self.assertContains(response, "Sam Reyes")
        user.refresh_from_db()
        other.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")
        self.assertEqual(user.contact_number, "+63 912 345 6789")
        self.assertFalse(user.is_staff)
        self.assertEqual(other.email, "other@example.com")

        response = self.client.post(reverse("edit_profile"), {"email": "OTHER@example.com"})
        self.assertTrue(response.context["form"].errors)
        user.refresh_from_db()
        self.assertEqual(user.email, "new@example.com")

    def test_logout_requires_csrf_token(self):
        client = Client(enforce_csrf_checks=True)
        client.force_login(self.make_user())
        self.assertEqual(client.post(reverse("logout")).status_code, 403)
