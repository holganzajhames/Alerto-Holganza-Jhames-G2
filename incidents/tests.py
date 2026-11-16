from io import StringIO

from django.contrib.auth import get_user_model
from django.core.management import call_command
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from .models import AlertReview, Notification, SOSReport


class SOSFlowTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        users = get_user_model()
        cls.student = users.objects.create_user("student", "student@example.com")
        cls.other = users.objects.create_user("other", "other@example.com")
        cls.reviewer = users.objects.create_user("reviewer", "reviewer@example.com", is_staff=True)
        cls.data = {"category": "medical", "location": "Main Hall", "description": "Demo incident."}

    def url(self, name, report=None):
        return reverse(f"incidents:{name}", args=[report.pk] if report else [])

    def submit(self, **fields):
        return self.client.post(self.url("create"), {**self.data, **fields}, follow=True)

    def make_report(self):
        return SOSReport.objects.create(reporter=self.student, **self.data)

    def test_student_crud_and_ownership(self):
        self.client.force_login(self.student)
        response = self.submit(latitude="0", longitude="123.456789", location_accuracy_m="10.5",
                               reporter=self.other.pk, status="confirmed")
        self.assertContains(response, "SOS report submitted.")
        report = SOSReport.objects.get()
        self.assertEqual(report.reporter, self.student)
        self.assertEqual(report.status, SOSReport.Status.UNVERIFIED)
        self.assertEqual(report.location_status, "available")
        self.assertContains(self.client.get(self.url("list")), "Main Hall")
        self.assertContains(self.client.get(self.url("detail", report)), "Approximate GPS coordinates")

        self.client.force_login(self.other)
        self.assertNotContains(self.client.get(self.url("list")), "Main Hall")
        for name in ("detail", "edit", "delete"):
            self.assertEqual(self.client.get(self.url(name, report)).status_code, 404)
        self.assertEqual(self.client.post(self.url("edit", report), self.data).status_code, 404)
        self.assertEqual(self.client.post(self.url("delete", report)).status_code, 404)

        self.client.force_login(self.student)
        self.assertContains(self.client.post(
            self.url("edit", report), {**self.data, "location": "Library"}, follow=True,
        ), "SOS report updated.")
        report.refresh_from_db()
        self.assertEqual(report.location, "Library")
        self.assertEqual(report.location_status, "unavailable")
        self.assertContains(self.client.get(self.url("delete", report)), "permanently removes")
        self.assertTrue(SOSReport.objects.filter(pk=report.pk).exists())
        self.assertContains(self.client.post(self.url("delete", report), follow=True), "SOS report deleted.")
        self.assertFalse(SOSReport.objects.filter(pk=report.pk).exists())

    def test_validation_errors(self):
        self.client.force_login(self.student)
        cases = [
            ({"location": " "}, "location"),
            ({"category": "unexpected"}, "category"),
            ({"latitude": "90.1", "longitude": "123"}, "latitude"),
            ({"longitude": "123"}, "latitude"),
            ({"location_accuracy_m": "10"}, "location_accuracy_m"),
        ]
        for fields, key in cases:
            with self.subTest(fields=fields):
                response = self.submit(**fields)
                self.assertIn(key, response.context["form"].errors)
        self.assertFalse(SOSReport.objects.exists())

    def test_review_finalizes_once_and_locks_student_mutations(self):
        report = self.make_report()
        self.client.force_login(self.reviewer)
        self.assertContains(self.client.get(self.url("review_list")), "Main Hall")
        self.assertContains(self.client.get(self.url("review_detail", report)), "Save decision")
        review_url = self.url("review_detail", report)
        self.assertContains(self.client.post(review_url, {"decision": "confirmed"}, follow=True),
                            "SOS report confirmed.")
        self.assertContains(self.client.post(review_url, {"decision": "dismissed"}, follow=True),
                            "already been reviewed")
        report.refresh_from_db()
        self.assertEqual(report.status, SOSReport.Status.CONFIRMED)
        self.assertEqual(AlertReview.objects.get(report=report).reviewer, self.reviewer)
        self.assertEqual(Notification.objects.filter(report=report).count(), 1)

        self.client.force_login(self.student)
        self.assertContains(self.client.get(self.url("detail", report)), "Confirmed")
        self.assertContains(self.client.post(self.url("edit", report), self.data, follow=True), "no longer be edited")
        self.assertContains(self.client.post(self.url("delete", report), follow=True), "no longer be deleted")

    def test_dismissal_creates_no_notification(self):
        report = self.make_report()
        self.client.force_login(self.reviewer)
        url = self.url("review_detail", report)
        response = self.client.post(url, {"decision": "invalid"})
        self.assertIn("decision", response.context["form"].errors)
        self.assertFalse(AlertReview.objects.exists())
        self.client.post(url, {"decision": "dismissed", "remarks": "Duplicate test entry."})
        report.refresh_from_db()
        self.assertEqual(report.status, SOSReport.Status.DISMISSED)
        self.assertFalse(Notification.objects.exists())

    def test_roles_and_csrf(self):
        report = self.make_report()
        self.assertRedirects(self.client.get(self.url("list")), "/login/?next=/incidents/")
        self.client.force_login(self.student)
        self.assertEqual(self.client.get(self.url("review_list")).status_code, 403)
        self.assertEqual(self.client.post(self.url("review_detail", report), {"decision": "confirmed"}).status_code, 403)
        self.client.force_login(self.reviewer)
        self.assertEqual(self.client.post(self.url("create"), self.data).status_code, 403)
        secure_client = Client(enforce_csrf_checks=True)
        secure_client.force_login(self.student)
        self.assertEqual(secure_client.post(self.url("delete", report)).status_code, 403)

    @override_settings(DEBUG=True)
    def test_demo_accounts_seed_and_sign_in(self):
        output = StringIO()
        call_command("seed_pd2_demo", confirm_demo_database=True, stdout=output)
        credentials = dict(line.split() for line in output.getvalue().splitlines())
        call_command("seed_pd2_demo", confirm_demo_database=True, stdout=StringIO())
        for username, title in [
            ("pd2_student", "Student dashboard"),
            ("pd2_reviewer", "Administrator dashboard"),
        ]:
            self.client.logout()
            response = self.client.post(reverse("login"), {
                "username": username, "password": credentials[username],
            }, follow=True)
            self.assertContains(response, title)
