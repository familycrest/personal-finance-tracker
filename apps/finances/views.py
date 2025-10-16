# finances/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Entry,
    Category,
    EntryType,
    AccountGoal,
    CategoryGoal,
)  # Layla added CategoryGoal because it imports the models from finance/models.py
from .forms import CategoryForm

from django.utils import timezone


@login_required
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


@login_required
def transactions(request):
    if request.method == "POST":
        date = request.POST.get("date")
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        entry_type = request.POST.get("entry_type")
        category_name = request.POST.get("category", "").strip()  # used to be category_id
        description = request.POST.get("description", "")

        # make sure all data items are given by user before saving
        if date and name and amount:

            # old code: category = Category.objects.get(id=category_id) if category_id else None
            # this gets the user's entered category or creates a new one
            if category_name:
                category, _ = Category.objects.get_or_create(
                    name=category_name,
                    user=request.user
                )

            # create the entries by the user
            Entry.objects.create(
                user=request.user,
                date=date,
                name=name,
                amount=amount,
                entry_type=entry_type,
                category=category,
                description=description,
            )
            return redirect("reports")  # will need to redirect this to transactions once pages merge

    categories = Category.objects.filter(user=request.user)

    context = {
        "categories": categories,
        "entry_types": EntryType.choices,
    }
    return render(request, "finances/transactions.html", context)


# create view for output of transaction entries
@login_required
def reports(request):
    reports_transactions = Entry.objects.filter(user=request.user).order_by("-date")
    return render(
        request, "finances/reports.html", {"reports_transactions": reports_transactions}
    )


# add functionality to delete transactions if the user wants
@login_required
def delete_transactions(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("reports")


# add functionality to edit transactions.
@login_required
def edit_transactions(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)

    if request.method == "POST":
        entry.date = request.POST.get("date")
        entry.name = request.POST.get("name")
        entry.amount = request.POST.get("amount")
        entry.entry_type = request.POST.get("entry_type")
        entry.description = request.POST.get("description", "")

        # changed from category_id to category_name to display name / may be possible to change back if needed
        category_name = request.POST.get("category", "").strip()  # strips leading characters from category name

        # old code:  entry.category = (
        # old code:    Category.objects.filter(id=category_id).first() if category_id else None)
        if category_name:
            # old code: entry.category = Category.objects.get(id=category_id, user=request.user)
            # old code: this gets the user's entered category or creates a new one
            category, created = Category.objects.get_or_create(
                name=category_name,
                user=request.user
            )
            entry.category = category

        else:
            entry.category = None

        # save entries and go back to reports
        entry.save()
        return redirect("reports")

    # gathers all categories for logged-in user to display
    # not needed for edit, but may be needed for display on categories.html
    # old code: categories = Category.objects.filter(user=request.user)

    return render(
        request,
        "finances/edit_transactions.html",
        {
            "entry": entry,
            # "categories": categories, # No longer needed because use inputs their own categories
            "entry_types": EntryType.choices,
        },
    )


# add a separate section to edit the category
@login_required
def edit_category(request, category_id):
    category = get_object_or_404(Category, id=category_id, user=request.user)

    if request.method == "POST":
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            return redirect("categories")  # or your category list page
    else:
        form = CategoryForm(instance=category)

    return render(request, "finances/edit_category.html", {"form": form, "category": category})
