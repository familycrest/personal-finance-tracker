# finances/views.py
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages

# import the sum module so the date range can be calulated
from django.db.models import Sum

from .models import (
    Entry,
    Category,
    EntryType,
    AccountGoal,
    CategoryGoal,
)  # Layla added CategoryGoal because it imports the models from finance/models.py
from .forms import CategoryForm

from django.utils import timezone

# create a dashboard view to hold the time-period-sidebar
@login_required
def dashboard(request):
    # this section begins the dashboard totals sidebar
    entries = Entry.objects.filter(user=request.user).order_by('-date')

    # get date ranges from sidebar
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # filter out date range with a start date and end date
    if start_date:
        entries = entries.filter(date__gte=start_date)
    if end_date:
        entries = entries.filter(date__lte=end_date)

    # calculate totals for income and expenses based on entry type
    income_total = entries.filter(entry_type="INCOME").aggregate(total=Sum('amount'))['total'] or 0
    expense_total = entries.filter(entry_type="EXPENSE").aggregate(total=Sum('amount'))['total'] or 0
    net_total = income_total - expense_total

    # pass the variables from the view to the template
    context = {
        "categories": categories,
        "entry_types": EntryType.choices,  # use EntryType.choices for GET requests
        "entries": entries,
        "income_total": income_total,
        "expense_total": expense_total,
        "net_total": net_total,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "dashboard.html", context)

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
    categories = Category.objects.filter(user=request.user)

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
            # redirect back to the same page
            return redirect("transactions")

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
        category_id = request.POST.get("category")
        entry.category = (
            Category.objects.filter(id=category_id).first() if category_id else None
        )
        entry.description = request.POST.get("description", "")

        # save entries and go back to reports
        entry.save()
        return redirect("reports")

    categories = Category.objects.filter(user=request.user)
    return render(
        request,
        "finances/edit_transactions.html",
        {
            "entry": entry,
            "categories": categories,
            "entry_types": EntryType.choices,
        },
    )
