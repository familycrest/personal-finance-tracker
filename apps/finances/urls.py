from django.urls import path
from apps.finances import views


# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("transactions/", views.view_transactions, name="view_transactions"),
    path("transactions/create", views.create_transaction, name="create_transaction"),
    path("reports/", views.reports, name="reports"),
    path(
        "transactions/edit/<int:entry_id>/",
        views.edit_transaction,
        name="edit_transaction",
    ),
    path(
        "transactions/delete/<int:entry_id>/",
        views.delete_transaction,
        name="delete_transaction",
    ),
    path("categories/", views.categories, name="categories"),
    path(
        "categories/delete/<int:category_id>/",
        views.delete_category,
        name="delete_category",
    ),
]
