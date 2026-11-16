from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView, LogoutView
from django.core.exceptions import PermissionDenied
from django.shortcuts import redirect, render
from django.urls import reverse

from .forms import ProfileForm, RegistrationForm, save_account_form
from .models import User


class AccountLoginView(LoginView):
    redirect_authenticated_user = True

    def get_success_url(self):
        return reverse("dashboard")


class AccountLogoutView(LogoutView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        messages.success(request, "You have been signed out.")
        return response


def register(request):
    if request.user.is_authenticated:
        return redirect("dashboard")

    form = RegistrationForm(request.POST if request.method == "POST" else None)
    if request.method == "POST" and form.is_valid() and save_account_form(form):
        messages.success(request, "Account created. You can now sign in.")
        return redirect("login")
    return render(request, "accounts/register.html", {"form": form})


@login_required
def dashboard(request):
    return redirect("admin_dashboard" if request.user.is_staff else "student_dashboard")


@login_required
def student_dashboard(request):
    if request.user.is_staff:
        raise PermissionDenied
    return render(request, "accounts/student_dashboard.html")


@login_required
def admin_dashboard(request):
    if not request.user.is_staff:
        raise PermissionDenied
    return render(request, "accounts/admin_dashboard.html", {
        "student_count": User.objects.filter(is_staff=False).count(),
    })


@login_required
def profile(request):
    return render(request, "accounts/profile.html")


@login_required
def edit_profile(request):
    form = ProfileForm(request.POST if request.method == "POST" else None, instance=request.user)
    if request.method == "POST" and form.is_valid() and save_account_form(form):
        messages.success(request, "Profile updated.")
        return redirect("profile")
    return render(request, "accounts/edit_profile.html", {"form": form})
