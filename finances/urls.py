# finances/urls.py
# from django.urls import path
from django.urls import path
from . import views

urlpatterns = [
    path("input_transaction/", views.input_transaction, name="input_transaction"),
    path("output_transaction/", views.output_transaction, name="output_transaction"),

]
