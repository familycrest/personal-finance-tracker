# finances/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path("transactions/", views.transactions, name="transactions"),
    path("reports/", views.reports, name="reports"),
    path("transactions/edit/<int:entry_id>/", views.edit_transactions, name="edit_transactions"),
    path("transactions/delete/<int:entry_id>/", views.delete_transactions, name="delete_transactions"),
]
