# finances/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import (
    Entry,
    Category,
    EntryType,
    Analytics,
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
def view_transactions(request):
    reports_transactions = Entry.objects.filter(user=request.user).order_by("-date")

    return render(
        request, "finances/view_transactions.html", {"reports_transactions": reports_transactions}
    )

@login_required
def create_transaction(request):
    if request.method == "POST":
        date = request.POST.get("date")
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        entry_type = request.POST.get("entry_type")
        category_id = request.POST.get("category")
        description = request.POST.get("description", "")

        # make sure all data items are given by user before saving
        if date and name and amount:
            category = Category.objects.get(id=category_id) if category_id else None

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
            return redirect("view_transactions")

    categories = Category.objects.filter(user=request.user)

    context = {
        "categories": categories,
        "entry_types": EntryType.choices,
    }
    return render(request, "finances/create_transaction.html", context)


# create view for output of transaction entries
@login_required
def reports(request):
    user = request.user
    analytics = Analytics.objects.filter(user_account=user).first()
    if analytics:
        Analytics.objects.all().delete()
    
    analytics = Analytics.objects.create(user_account=user)
    analytics.generate_account_report()
    
    reports = analytics.reports.all()

    return render(
        request, "finances/reports.html", {"reports": reports}
    )


# add functionality to delete transactions if the user wants
@login_required
def delete_transaction(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("view_transactions")


# add functionality to edit transactions.
@login_required
def edit_transaction(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    if request.method == "POST":
        entry.date = request.POST.get("date")
        entry.name = request.POST.get("name")
        entry.amount = request.POST.get("amount")
        entry.entry_type = request.POST.get("entry_type")
        category_id = request.POST.get("category")
        entry.category = (
            Category.objects.filter(id=category_id).first() if category_id else None
        )
        entry.description = request.POST.get("description", "")

        # save entries and go back to reports
        entry.save()
        return redirect("view_transactions")

    categories = Category.objects.filter(user=request.user)
    return render(
        request,
        "finances/edit_transaction.html",
        {
            "entry": entry,
            "categories": categories,
            "entry_types": EntryType.choices,
        },
    )
