from django.contrib import admin

from .models import User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    fieldsets = (
        (
            None,
            {"fields": ("name", "email", "password")},
        ),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        (
            "Dates",
            {"fields": ("last_login", "date_joined")},
        ),
    )
    readonly_fields = ("date_joined",)
    list_display = ("email", "name", "is_active", "is_staff", "is_superuser")
    search_fields = ("name", "email")
    ordering = ["email"]
