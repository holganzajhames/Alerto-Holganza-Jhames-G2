from django.contrib.auth.models import AbstractUser
from django.db import models
from django.db.models.functions import Lower


class User(AbstractUser):
    email = models.EmailField()
    contact_number = models.CharField(max_length=25, blank=True)

    REQUIRED_FIELDS = ["email"]

    class Meta:
        constraints = [
            models.UniqueConstraint(Lower("email"), name="accounts_email_ci_unique"),
            models.UniqueConstraint(Lower("username"), name="accounts_username_ci_unique"),
        ]
