from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from .models import Category
from .forms import CategoryForm


def categories(request):
    categories = Category.objects.filter(user=request.user)

    if request.method == "POST":
        category_id = request.POST.get("id")

        if category_id:
            category = get_object_or_404(Category, id=category_id, user=request.user)
            form = CategoryForm(request.POST, instance=category)
        else:
            form = CategoryForm(request.POST)

        if form.is_valid():
            category = form.save(commit=False)
            category.user = request.user
            category.save()
            return redirect("categories")
    else:
        form = CategoryForm()

    return render(
        request,
        "finances/categories.html",
        {"categories": categories, "form": form},
    )


def delete_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == "POST":
        category.delete()
        messages.success(request, f"Category '{category.name}' deleted sucessfully.")
        return redirect("categories")

    return redirect("categories")
