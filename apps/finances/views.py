from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Entry, Category, EntryType, AccountGoal, CategoryGoal  # import models
from .forms import CategoryForm, EntryForm, EntryFilterForm  # import forms
from django.db.models import Sum  # import the sum module so the date range can be calculated
from django.utils import timezone  # import timezone for date


# create a dashboard view to hold the time-period-sidebar
@login_required
def dashboard(request):
    # get the logged-in user
    user = request.user

    # show the 3 most recent transactions
    transactions_output = Entry.objects.filter(user=request.user).order_by('-date')[:3]

    # this section begins the dashboard totals sidebar.
    # gets all entries for user
    entries = Entry.objects.filter(user=request.user).order_by('-date')

    # get date ranges from sidebar
    start_date = request.GET.get('start_date')
    end_date = request.GET.get('end_date')

    # have the output values start at 0
    income_total = 0
    expense_total = 0
    net_total = 0

    # filter out date range with a start date and end date
    if start_date or end_date:
        if start_date:
            entries = entries.filter(date__gte=start_date)
        if end_date:
            entries = entries.filter(date__lte=end_date)

        # calculate totals for income and expenses based on entry type
        income_total = entries.filter(entry_type="INCOME").aggregate(total=Sum('amount'))['total'] or 0
        expense_total = entries.filter(entry_type="EXPENSE").aggregate(total=Sum('amount'))['total'] or 0
        net_total = income_total - expense_total

    categories = Category.objects.filter(user=user)

    # pass the variables from the view to the template
    context = {
        "transactions_output": transactions_output,
        "categories": categories,
        "entry_types": EntryType.choices,  # use EntryType.choices for GET requests
        "entries": entries,
        "income_total": income_total,
        "expense_total": expense_total,
        "net_total": net_total,
        "start_date": start_date,
        "end_date": end_date,
    }

    return render(request, "finances/dashboard.html", context)


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
    categories = Category.objects.filter(user=request.user)
    editing = False
    edit_id = None
    edit_id = request.GET.get("edit")
    entry = None

    # commented this out becasue the if statement does this and edits as well. 
    # leaving this in for now in case it needs to be restored.

    # if request.method == "POST":
    #     date = request.POST.get("date")
    #     name = request.POST.get("name")
    #     amount = request.POST.get("amount")
    #     entry_type = request.POST.get("entry_type")
    #     category_id = request.POST.get("category")
    #     description = request.POST.get("description", "")
    # # TODO: make this mess comprehensible!! maybe split into editing and non-editing branches, at the cost of violating DRY
    #
    #     # get the selected category
    #     category = Category.objects.filter(id=category_id, user=request.user).first()
    #
    #     # create the entries by the user
    #     Entry.objects.create(
    #         user=request.user,
    #         date=date,
    #         name=name,
    #         amount=amount,
    #         entry_type=entry_type,
    #         category=category,
    #         description=description,
    #     )
    #     # redirect back to the same page
    #     return redirect("transactions")
    #
    # # Default form
    # entry_form = EntryForm(initial={
    #     "date": datetime.today().strftime("%Y-%m-%d"),
    #     "entry_type": EntryType.EXPENSE,
    # })

    # if request.GET.get("edit"):
    #     edit_id = request.GET.get("edit")
    if edit_id:
        try:
            entry = Entry.objects.get(pk=edit_id)
            entry_form = EntryForm(instance=entry)
            editing = True
        except:
            entry_form.add_error(error=f"Could not find transaction {edit_id}")

    # Handle form submissions
    if request.method == "POST":
        # if editing:
        if editing and entry:
            entry_form = EntryForm(request.POST, instance=entry)
        else:
            entry_form = EntryForm(request.POST)

        if entry_form.is_valid():
            # if editing:
            saved_entry_form = entry_form.save(commit=False)
            saved_entry_form.user = request.user
            saved_entry_form.save()
            return redirect("transactions")

    else:
        # # Create a new entry from the form, without saving it to the server yet
        # new_entry = entry_form.save(commit=False)
        #
        # # Assign this entry to the current user and finally save it
        # new_entry.user = request.user
        # new_entry.save()
        #
        # return redirect("transactions")
        if editing and entry:
            entry_form = EntryForm(instance=entry)
        else:
            entry_form = EntryForm(initial={
                "date": datetime.today().strftime("%Y-%m-%d"),
                "entry_type": EntryType.EXPENSE,
            })

    # TODO: maybe encapsulate this in its own function
    # display the transaction and category entered by user
    # categories = Category.objects.filter(user=request.user)
    user_entries = Entry.objects.filter(user=request.user).order_by("-date")
    entries_output = user_entries

    # Big big big big big big thanks to https://stackoverflow.com/a/43096716/8746360
    # A bound form (one with the request given to it) does not have initial values
    if request.GET and EntryFilterForm.base_fields.keys():
        entry_filter_form = EntryFilterForm(request.GET)
    else:
        entry_filter_form = EntryFilterForm()

    if entry_filter_form.is_valid():
        filters = entry_filter_form.cleaned_data

        if filters["date_start"]:
            entries_output = entries_output.filter(
                date__gte=filters["date_start"]
            )

        if filters["date_end"]:
            entries_output = entries_output.filter(
                date__lte=filters["date_end"]
            )

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
        "edit_id": int(edit_id) if editing else None,
        "categories": categories,
        "entries_output": entries_output,
        # "add_form_data": {},  # avoid template errors
        "entry_form": entry_form,
        "entry_filter_form": entry_filter_form,
        "new_user": len(user_entries) == 0
    }

    return render(request, "finances/transactions.html", context)

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

        # save entries
        entry.save()

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

