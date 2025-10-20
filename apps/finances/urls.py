from django.urls import path
from apps.finances import views


# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("transactions/", views.transactions, name="transactions"),
    path("reports/", views.reports, name="reports"),
    path(
        "transactions/edit/<int:entry_id>/",
        views.edit_transactions,
        name="edit_transactions",
    ),
    path(
        "transactions/delete/<int:entry_id>/",
        views.delete_transactions,
        name="delete_transactions",
    ),
    path("categories/", views.categories, name="categories"),
    path(
        "categories/delete/<int:category_id>/",
        views.delete_category,
        name="delete_category",
    ),
    path("goals/", views.goals, name="goals"),
    path("goals/delete/", views.delete_goals, name="delete_goals"),
]
