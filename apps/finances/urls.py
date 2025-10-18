from django.urls import path
from apps.finances import views


# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("transactions/", views.transactions, name="transactions"),
    path("reports/", views.reports, name="reports"),

    # May need this later once category is worked on.
    # Temporarily removed edit_transactions because it's now edited on transactions page
    # path(
    #     "transactions/edit/<int:entry_id>/",
    #     views.edit_transactions,
    #     name="edit_transactions",
    # ),

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
    # uncomment when goals page is created:
    # path("goals/", views.goals, name="goals",)
]
