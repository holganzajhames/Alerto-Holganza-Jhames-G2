from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import User


@admin.register(User)
class AccountAdmin(UserAdmin):
    fieldsets = (*UserAdmin.fieldsets, ("Contact", {"fields": ("contact_number",)}))
    add_fieldsets = (*UserAdmin.add_fieldsets, ("Contact", {"fields": ("email", "contact_number")}))
