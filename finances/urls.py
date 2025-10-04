from django.urls import path
from finances import views


urlpatterns = [
    path("categories/", views.categories, name="categories"),
    path(
        "categories/delete/<int:category_id>/",
        views.delete_category,
        name="delete_category",
    ),
]
