from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .forms import CustomUserCreationForm, CustomUserChangeForm
from .models import User


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    # Fields for existing users
    list_display = ("email", "username", "first_name", "last_name", "is_staff")
    list_filter = ("is_staff", "is_superuser", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)

    # Fields for editing users
    fieldsets = (
            (None, {"fields": ("email", "password")}),
            ("Personal Info", {"fields": ("username", "first_name", "last_name")}),
            ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        )
    readonly_fields = ("created_at", "updated_at", "last_login")  # Show, don’t edit

    # Fields for adding users
    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": ("email", "username", "password1", "password2"),
        }),
    )

    # Fix password handling
    def save_model(self, request, obj, form, change):
        if not change:  # New user
            obj.set_password(form.cleaned_data["password1"])
        super().save_model(request, obj, form, change)