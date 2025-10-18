from django.contrib import admin

from .models import Category, Entry, Goal, AccountGoal, CategoryGoal


# ==========================
#  Category
# ==========================
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "entry_type")  # show name, user, entry_type
    search_fields = ("user__username", "name", "entry_type")  # allow searching by name, user, and entry_type
    list_filter = ("entry_type",)
    ordering = ("user", "name",)  # sort by user than name alphabetically


# ==========================
# Entry
# ==========================
@admin.register(Entry)
class EntryAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "category", "amount", "date", "entry_type")
    search_fields = ("user__username", "name", "category__name", "amount", "date", "entry_type")
    list_filter = ("amount", "entry_type", "date")  # add sidebar filters
    ordering = ("-date",)  # newest first


# ============================
# Goal
# ============================
@admin.register(AccountGoal)
class AccountGoalAdmin(admin.ModelAdmin):
    list_display = ("user", "name", "start_date", "end_date", "amount", "entry_type", "progress")
    search_fields = ("user__username", "name", "start_date", "end_date", "amount", "entry_type")
    list_filter = ("start_date", "end_date")


@admin.register(CategoryGoal)
class CategoryGoalAdmin(admin.ModelAdmin):
    list_display = ("category", "name", "start_date", "end_date", "amount", "entry_type", "progress")
    search_fields = ("category__name", "name", "start_date", "end_date", "amount", "entry_type")
    list_filter = ("start_date", "end_date")
