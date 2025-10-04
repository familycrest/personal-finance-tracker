# finances/views.py

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required

from .models import Entry, Category, EntryType, AccountGoal, CategoryGoal  # Layla added CategoryGoal because it imports the models from finance/models.py
from django.utils import timezone


# Create your views here.
@login_required
def transactions(request):
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
            return redirect("reports")

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
    return render(request, "finances/reports.html", {"reports_transactions": reports_transactions})


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
        category_id = request.POST.get("category")
        entry.category = Category.objects.filter(id=category_id).first() if category_id else None
        entry.description = request.POST.get("description", "")

        # save entries and go back to reports
        entry.save()
        return redirect("reports")

    categories = Category.objects.filter(user=request.user)
    return render(request, "finances/edit_transactions.html", {
        "entry": entry,
        "categories": categories,
        "entry_types": EntryType.choices,
    })
