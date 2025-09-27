# Import Django's built-in admin interface
from django.contrib import admin

# Import the UserAdmin class so we can customize how user accounts are displayed in the admin
from django.contrib.auth.admin import UserAdmin

# Import our custom models from models.py
from .models import (
    UserAccount, Category, Entry, Goal, 
    CategoryBudgetGoal, CategoryIncomeGoal, 
    AccountBudgetGoal, AccountIncomeGoal, 
    Notification
)

# =======================
# UserAccount 
#========================
@admin.register(UserAccount)
class UserAccountAdmin(UserAdmin):
    model = UserAccount
    # Fields shown in the list view of Accounts in the admin panel
    list_display = ("username", "email", "is_staff", "is_active")

    # Fields we can search by in the admin search bar
    search_fields = ("username", "email")

    list_filter = ("is_staff", "is_active")

    # Default ordering of Accounts in the admin list view
    ordering = ("id",)

#==========================
#  Category
#==========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "entry_type") # show ID and categoy name
    search_fields = ("name",)  # allow searching by name
    ordering = ("name",)    # alphabetical

#==========================
# Entry
#==========================
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "category", "amount", "date", "entry_type")
    search_fields = ("name", "description") 
    list_filter = ("entry_type", "date")   # add sidebar filters
    ordering = ("-date",)   # newest first

#============================
# Goal
#============================
@admin.register(Goal)
class GoalAdmin(admin.ModelAdmin):
    list_display = ("name", "user", "start_date", "end_date", "progress")
    search_fields = ("name", "description")
    list_filter = ("start_date", "end_date")


#============================
#Notification 
#============================
@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ("title", "user", "notification_type", "is_read", "creation_date")
    search_fields = ("title", "message") # Search by user or message text
    list_filter = ("notification_type", "is_read")   # Filter by read/unread, date
    ordering = ("-creation_date",)  # latest notification first

#===================================================
#New Part: Goal subclasses (each has its own admin)
#====================================================
@admin.register(CategoryBudgetGoal)
class CategoryBudgetGoalAdmin(GoalAdmin):
    list_display = ("name", "user", "category", "start_date", "end_date", "progress" )

@admin.register(CategoryIncomeGoal)
class CategoryIncomeGoalAdmin(GoalAdmin):
    list_display = ("name", "user", "category", "start_date", "end_date", "progress" )

@admin.register(AccountBudgetGoal)
class AccountBudgetGoalAdmin(GoalAdmin):
    list_display = ("name", "user_account", "start_date", "end_date", "progress" )

@admin.register(AccountIncomeGoal)
class AccountIncomeGoalAdmin(GoalAdmin):
    list_display = ("name", "user_account", "start_date", "end_date", "progress" )


