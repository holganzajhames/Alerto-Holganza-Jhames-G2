from django.conf import settings
from django.db import models


class SOSReport(models.Model):
    class Category(models.TextChoices):
        MEDICAL = "medical", "Medical emergency"
        SECURITY = "security", "Security concern"
        FIRE = "fire", "Fire or smoke"
        OTHER = "other", "Other incident"

    class Status(models.TextChoices):
        UNVERIFIED = "unverified", "Unverified"
        CONFIRMED = "confirmed", "Confirmed"
        DISMISSED = "dismissed", "Dismissed"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sos_reports",
    )
    category = models.CharField(max_length=12, choices=Category.choices)
    location = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    location_accuracy_m = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    location_status = models.GeneratedField(
        expression=models.Case(
            models.When(latitude__isnull=False, longitude__isnull=False, then=models.Value("available")),
            default=models.Value("unavailable"),
        ),
        output_field=models.CharField(max_length=11),
        db_persist=True,
    )
    status = models.CharField(max_length=12, choices=Status.choices, default=Status.UNVERIFIED)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")
        constraints = [
            models.CheckConstraint(
                condition=(
                    models.Q(latitude__isnull=True, longitude__isnull=True, location_accuracy_m__isnull=True)
                    | models.Q(latitude__isnull=False, longitude__isnull=False,
                               latitude__range=(-90, 90), longitude__range=(-180, 180))
                ),
                name="incidents_gps_pair_in_range",
            ),
            models.CheckConstraint(
                condition=models.Q(location_accuracy_m__gte=0) | models.Q(location_accuracy_m__isnull=True),
                name="incidents_accuracy_nonnegative",
            ),
            models.CheckConstraint(
                condition=models.Q(status__in=["unverified", "confirmed", "dismissed"]),
                name="incidents_status_valid",
            ),
        ]


class AlertReview(models.Model):
    class Decision(models.TextChoices):
        CONFIRMED = "confirmed", "Confirm"
        DISMISSED = "dismissed", "Dismiss"

    report = models.OneToOneField(SOSReport, on_delete=models.PROTECT, related_name="review")
    reviewer = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="alert_reviews",
    )
    decision = models.CharField(max_length=12, choices=Decision.choices)
    remarks = models.CharField(max_length=500, blank=True)
    reviewed_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        constraints = [
            models.CheckConstraint(
                condition=models.Q(decision__in=["confirmed", "dismissed"]),
                name="incidents_review_decision_valid",
            ),
        ]


class Notification(models.Model):
    report = models.OneToOneField(SOSReport, on_delete=models.PROTECT, related_name="notification")
    title = models.CharField(max_length=120)
    message = models.CharField(max_length=500)
    created_at = models.DateTimeField(auto_now_add=True)
