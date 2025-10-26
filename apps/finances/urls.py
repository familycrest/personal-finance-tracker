from django.urls import path
from apps.finances import views


# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("dashboard/", views.dashboard, name="dashboard"),
    path("transactions/", views.transactions, name="transactions"),
    path(
        "transactions/delete/<int:entry_id>/",
        views.delete_transactions,
        name="delete_transactions",
    ),
    path("reports/", views.reports, name="reports"),
    # create a url path to edit_transactions and redirect back to transactions

    path("categories/", views.categories, name="categories"),
    path(
        "categories/delete/<int:category_id>/",
        views.delete_category,
        name="delete_category",
    ),
    # uncomment when goals page is created:
    # path("goals/", views.goals, name="goals",)

]