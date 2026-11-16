from secrets import token_urlsafe

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.management.base import BaseCommand, CommandError
from django.db import transaction


DEMO_ACCOUNTS = (
    ("pd2_student", "pd2.student@example.com", False),
    ("pd2_reviewer", "pd2.reviewer@example.com", True),
)


class Command(BaseCommand):
    help = "Create the report's demo accounts in a disposable Django database."

    def add_arguments(self, parser):
        parser.add_argument("--confirm-demo-database", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if not settings.DEBUG or not options["confirm_demo_database"]:
            raise CommandError("Use DEBUG and --confirm-demo-database with a disposable demo database.")
        users = get_user_model()
        credentials = []
        for username, email, is_staff in DEMO_ACCOUNTS:
            user, created = users.objects.get_or_create(
                username=username, defaults={"email": email, "is_staff": is_staff},
            )
            if created:
                password = token_urlsafe(20)
                user.set_password(password)
                credentials.append(f"{username} {password}")
                user.save(update_fields=["password"])
            elif (
                user.email != email or user.is_staff != is_staff or user.is_superuser
                or not user.is_active
            ):
                raise CommandError(f"{username} already belongs to a different account.")
        if credentials:
            self.stdout.write("\n".join(credentials))
        else:
            self.stdout.write("PD2 demo accounts already exist. Use their original passwords.")
