# Import Django's built-in admin interface
from django.contrib import admin

# Import the UserAdmin classs so we can customize how user accounts are displayed in the admin
from django.contrib.auth.admin import UserAdmin

# Import our custom models from models.py
from .models import Account, Category, Entry, Goal, Notification

# Account model with Username
@admin.register(Account)
class AccountAdmin(UserAdmin):

    # Fields shown in the list view of Accounts in the admin panel
    list_display = ("username", "email", "first_name", "last_name", "is_staff")

    # Fields we can search by in the admin search bar
    search_fields = ("username", "email", "first_name", "last_name")

    # Default ordering of Accounts in the admin list view
    ordering = ("id",)

# Customize the Category model
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "entry_type") # show ID and categoy name
    search_fields = ("name", "description")     # allow searching by name

# Customize the Entry model (transactions)
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("id", "name", "description", "entry_type", "date", "amount")
    list_filter = ("entry_type", "date")   # add sidebar filters
    searh_filedds = ("name", "description")  # search by realted fileds

# Customize the Goal model
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("id", "account", "name", "target_amount", "current_amount", "deadline")
    list_filter = ("deadline",)
    search_fields = ("name", "description")

# Customize the Notification model
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("id", "title", "message", "notification_type", "creation_date")
    list_filter = ("notification_type", "creation_date")         # Filter by read/unread, date
    search_fields = ("title", "message") # Search by user or message text



