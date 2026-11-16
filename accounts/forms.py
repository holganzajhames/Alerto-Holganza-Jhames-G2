from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.validators import RegexValidator
from django.db import IntegrityError, transaction

from .models import User


class RegistrationForm(UserCreationForm):
    class Meta(UserCreationForm.Meta):
        model = User
        fields = ("username", "email")

    def clean_email(self):
        return self.cleaned_data["email"].lower()


class ProfileForm(forms.ModelForm):
    contact_number = forms.CharField(
        max_length=25,
        required=False,
        validators=[RegexValidator(
            r"^\+?[0-9][0-9 ()-]*$",
            "Enter a phone number using digits, spaces, parentheses, or hyphens.",
        )],
        widget=forms.TextInput(attrs={"type": "tel", "autocomplete": "tel"}),
    )

    class Meta:
        model = User
        fields = ("first_name", "last_name", "email", "contact_number")

    def clean_email(self):
        return self.cleaned_data["email"].lower()


def save_account_form(form):
    try:
        with transaction.atomic():
            form.save()
    except IntegrityError as error:
        constraint = getattr(getattr(error.__cause__, "diag", None), "constraint_name", None)
        duplicate_fields = {
            "accounts_email_ci_unique": "email",
            "accounts_username_ci_unique": "username",
            "accounts_user_username_key": "username",
        }
        if constraint not in duplicate_fields:
            raise
        field = duplicate_fields[constraint]
        form.add_error(field, f"This {field} is already in use.")
        return False
    return True
