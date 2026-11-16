from django.conf import settings
from django.db import models


class SOSReport(models.Model):
    class Category(models.TextChoices):
        MEDICAL = "medical", "Medical emergency"
        SECURITY = "security", "Security concern"
        FIRE = "fire", "Fire or smoke"
        OTHER = "other", "Other incident"

    reporter = models.ForeignKey(
        settings.AUTH_USER_MODEL, on_delete=models.PROTECT, related_name="sos_reports",
    )
    category = models.CharField(max_length=12, choices=Category.choices)
    location = models.CharField(max_length=150)
    description = models.TextField(max_length=2000)
    latitude = models.DecimalField(max_digits=8, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ("-created_at", "-pk")
