from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# added CategoryGoal because it imports the models from finance/models.py
from django.utils import timezone

from .models import Entry, Category, EntryType, AccountGoal, CategoryGoal
from .forms import CategoryForm, EntryForm, EntryFilterForm

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

# create view to add, list, and filter transactions
@login_required
def transactions(request):
    # Default forms
    entry_form = EntryForm(initial={
        "date": datetime.today().strftime("%Y-%m-%d"),
        "entry_type": EntryType.EXPENSE
    })

    # Handle form submissions
    if request.method == "POST": 
        entry_form = EntryForm(request.POST)

        if entry_form.is_valid():
            # Create a new entry from the form, without saving it to the server yet
            new_entry = entry_form.save(commit=False)
            
            # Assign this entry to the current user and finally save it
            new_entry.user = request.user
            new_entry.save()

            return redirect("transactions")

    # display the transaction and category entered by user
    categories = Category.objects.filter(user=request.user)
    entries_output = Entry.objects.filter(user=request.user).order_by("-date")

    # Big big big big big big thanks to https://stackoverflow.com/a/43096716/8746360
    # A bound form (one with the request given to it) does not have initial values
    if request.GET & EntryFilterForm.base_fields.keys():
        entry_filter_form = EntryFilterForm(request.GET)
    else:
        entry_filter_form = EntryFilterForm()
    
    if entry_filter_form.is_valid():
        filters = entry_filter_form.cleaned_data

        if filters["date"]:
            entries_output = entries_output.filter(date=filters["date"])

        if filters["name"]:
            entries_output = entries_output.filter(name__icontains=filters["name"])

        if filters["amount"]:
            try:
                entries_output = entries_output.filter(amount=float(filters["amount"]))
            except ValueError:
                pass

        # Include all entries by default, only exclude if the checkbox is not checked
        if not filters["entry_type_income"]:
            entries_output = entries_output.exclude(entry_type=EntryType.INCOME)
            
        if not filters["entry_type_expense"]:
            entries_output = entries_output.exclude(entry_type=EntryType.EXPENSE)

        if filters["category"]:
            entries_output = entries_output.filter(category_id=filters["category"])

    context = {
        "categories": categories,
        "entries_output": entries_output,
        "add_form_data": {},  # avoid template errors
        "entry_form": entry_form,
        "entry_filter_form": entry_filter_form
    }

    return render(request, "finances/transactions.html", context)

# add functionality to delete transactions if the user wants
@login_required
def delete_transactions(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("transactions")


# create a separate view to edit transactions
@login_required
def edit_transactions(request, entry_id):
    # Ensure entry_id is an integer
    try:
        entry_id = int(entry_id)
    except (ValueError, TypeError):
        return redirect("transactions")

    entry = get_object_or_404(Entry, id=entry_id, user=request.user)

    if request.method == "POST":
        entry.date = request.POST.get("date")
        entry.name = request.POST.get("name")

        try:
            entry.amount = float(request.POST.get("amount"))
        except (TypeError, ValueError):
            entry.amount = 0

        entry.amount = request.POST.get("amount")
        entry.entry_type = request.POST.get("entry_type")
        category_id = request.POST.get("category")
        entry.category = (Category.objects.filter(id=category_id, user=request.user).first() if category_id else None)
        entry.description = request.POST.get("description", "")

        # save entries and go back to reports
        entry.save()
        return redirect("transactions")

    categories = Category.objects.filter(user=request.user)
    context = {
        "entry": entry,
        "categories": categories,
        "entry_types": EntryType.choices,
    }
    return render(request, "finances/edit_transactions.html", context)

# create view for output of transaction entries
@login_required
def reports(request):
    reports_transactions = Entry.objects.filter(user=request.user).order_by("-date")
    return render(
        request, "finances/reports.html", {"reports_transactions": reports_transactions}
    )

# create dashboard view to show sidebars
@login_required
def dashboard(request):
    # show the 3 most recent transactions
    transactions_output = Entry.objects.filter(user=request.user).order_by('-date')[:3]

    context = {
        "transactions_output": transactions_output,
    }

    return render(request, "finances/dashboard.html", context)
