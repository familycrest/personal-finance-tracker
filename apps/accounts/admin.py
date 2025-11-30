# Import Django's built-in admin interface
from django.contrib import admin

# Import the UserAdmin class so we can customize how user accounts are displayed in the admin
from django.contrib.auth.admin import UserAdmin

# Import our custom models from models.py
from .models import UserAccount


# =======================
# UserAccount
# ========================
@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin):
    # Fields shown in the list view of Accounts in the admin panel
    list_display = (
        "username",
        "email",
        "is_staff",
        "is_active",
    )

    # Fields we can search by in the admin search bar
    search_fields = ("username", "email")

    list_filter = ("is_staff", "is_active")

    # Default ordering of Accounts in the admin list view
    ordering = ("username", "email")
