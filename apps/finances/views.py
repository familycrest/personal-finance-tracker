# finances/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
# added CategoryGoal because it imports the models from finance/models.py
from .models import (Entry, Category, EntryType, AccountGoal, CategoryGoal)
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

# create view to add, list, and filter transactions
@login_required
def transactions(request):
    # section for adding a new transaction
    if request.method == "POST":
        date = request.POST.get("date")
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        entry_type = request.POST.get("entry_type")
        category_id = request.POST.get("category")
        description = request.POST.get("description", "")

        # create a transaction entry even if category isn't selected
        if date and name and amount:
            category = Category.objects.filter(id=category_id, user=request.user).first() if category_id else None
            Entry.objects.create(
                user=request.user,
                date=date,
                name=name,
                amount=amount,
                entry_type=entry_type,
                category=category,
                description=description,
            )
            return redirect("transactions")

    # display the transaction and category entered by user
    categories = Category.objects.filter(user=request.user)
    transactions_output = Entry.objects.filter(user=request.user).order_by("-date")

    # include filtering section
    filter_date = request.GET.get("filter_date")
    filter_name = request.GET.get("filter_name")
    filter_amount = request.GET.get("filter_amount")
    filter_type = request.GET.get("filter_type")
    filter_category = request.GET.get("filter_category")

    if filter_date:
        transactions_output = transactions_output.filter(date=filter_date)
    if filter_name:
        transactions_output = transactions_output.filter(name__icontains=filter_name)
    if filter_amount:
        try:
            transactions_output = transactions_output.filter(amount=float(filter_amount))
        except ValueError:
            pass
    if filter_type:
        transactions_output = transactions_output.filter(entry_type=filter_type)

    if filter_category:
        transactions_output = transactions_output.filter(category_id=filter_category)

    context = {
        "categories": categories,
        "entry_types": EntryType.choices,
        "transactions_output": transactions_output,
        "filter_date": filter_date,
        "filter_name": filter_name,
        "filter_amount": filter_amount,
        "filter_type": filter_type,
        "filter_category": filter_category,
        "add_form_data": {},  # avoid template errors

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
