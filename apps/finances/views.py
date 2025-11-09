from datetime import datetime

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from .models import Entry, Category, EntryType, AccountGoal, CategoryGoal  # import models
from .forms import (  # import forms
    CategoryForm,
    EntryForm,
    EntryFilterForm,
    AddAccountGoalForm,
    EditAccountGoalForm,
    AddCategoryGoalForm,
    EditCategoryGoalForm,
    )
from django.db.models import Sum  # import the sum module so the date range can be calculated
from django.http import JsonResponse
import json


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

    if edit_id:
        try:
            entry = Entry.objects.get(pk=edit_id, user=request.user)
            entry_form = EntryForm(instance=entry)
            editing = True
        except Entry.DoesNotExist:
            # If editing but the entry doesn't exist redirect to the transactions page
            return redirect("transactions")

    # Handle form submissions
    if request.method == "POST":
        # if editing:
        if editing:
            entry_form = EntryForm(request.POST, instance=entry)
        else:
            entry_form = EntryForm(request.POST)

        # Check if form for adding a new entry or editing an existing entry is valid then save
        if entry_form.is_valid():
                saved_entry_form = entry_form.save(commit=False)
                saved_entry_form.user = request.user
                saved_entry_form.save()
                return redirect("transactions")

    # Handle get requests
    else:
        # Create a new entry from the form, without saving it to the server yet
        if editing:
            entry_form = EntryForm(instance=entry)
        else:
            entry_form = EntryForm(initial={
                "date": datetime.today().strftime("%Y-%m-%d"),
                "entry_type": EntryType.EXPENSE,
            })

    # Create list of transactions to show to the user. This one is a separate list from the
    # latter for the template to know if the user has any transactions at all.
    user_entries = Entry.objects.filter(user=request.user).order_by("-date")
    # Creates a separate list of user transactions to filter.
    entries_output = user_entries

    # Big big big big big big thanks to https://stackoverflow.com/a/43096716/8746360
    # A bound form (one with the request given to it) does not have initial values
    filter_params = {k: v for k, v in request.GET.items() if k != 'edit'}

    if filter_params and EntryFilterForm.base_fields.keys():
        entry_filter_form = EntryFilterForm(filter_params)
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

# add functionality to delete transactions if the user wants
@login_required
def delete_transactions(request, entry_id):
    entry = get_object_or_404(Entry, id=entry_id, user=request.user)
    entry.delete()
    return redirect("transactions")


# create view for output of transaction entries
@login_required
def reports(request):
    reports_transactions = Entry.objects.filter(user=request.user).order_by("-date")
    return render(
        request, "finances/reports.html", {"reports_transactions": reports_transactions}
    )


@login_required
def goals(request):
    """
    View for CRUD operations for AccountGoals and CategoryGoals.
    """
    # Whether each dialog is visible on page load, in case of form error
    acct_goal_add = False
    acct_goal_edit = False
    cat_goal_add = False
    cat_goal_edit = False

    user = request.user
    # Goal being edited
    editing_goal = None

    # Check if we're editing via query parameter (GET) or hidden field (POST)
    edit_id = request.GET.get("goal-id") or request.POST.get("goal-id")
    form_type = request.GET.get("form_type") or request.POST.get("form_type")

    if edit_id and form_type:
        try:
            # Check if editing account goal
            if form_type == "edit-acct-goal":
                editing_goal = AccountGoal.objects.get(pk=edit_id, user=user)
            # Check if editing category goal
            elif form_type == "edit-cat-goal":
                editing_goal = CategoryGoal.objects.get(pk=edit_id, category__user=user)
        except (AccountGoal.DoesNotExist, CategoryGoal.DoesNotExist):
            return redirect("goals")
    
    # Handle post requests, accept forms to add a new goal or edit an existing goal
    if request.method == "POST":
        # Initialize all forms as None
        add_account_goal_form = None
        edit_account_goal_form = None
        add_category_goal_form = None
        edit_category_goal_form = None

        # Process the submitted form
        if form_type == "edit-acct-goal" and editing_goal:
            edit_account_goal_form = EditAccountGoalForm(request.POST, instance=editing_goal, user=user)
            if edit_account_goal_form.is_valid():
                edit_account_goal_form.save()
                return redirect("goals")
            acct_goal_edit = True

        elif form_type == "edit-cat-goal" and editing_goal:
            edit_category_goal_form = EditCategoryGoalForm(request.POST, instance=editing_goal, user=user)
            if edit_category_goal_form.is_valid():
                edit_category_goal_form.save()
                return redirect("goals")
            cat_goal_edit = True

        elif form_type == "add-acct-goal":
            add_account_goal_form = AddAccountGoalForm(request.POST, user=user)
            if add_account_goal_form.is_valid():
                add_account_goal_form.save()
                return redirect("goals")
            acct_goal_add = True

        elif form_type == "add-cat-goal":
            add_category_goal_form = AddCategoryGoalForm(request.POST, user=user)
            if add_category_goal_form.is_valid():
                add_category_goal_form.save()
                return redirect("goals")
            cat_goal_add = True

        # Ensure all forms are defined (create empty ones for forms that weren't submitted)
        if add_account_goal_form is None:
            add_account_goal_form = AddAccountGoalForm(user=user)
        if edit_account_goal_form is None:
            edit_account_goal_form = EditAccountGoalForm(user=user)
        if add_category_goal_form is None:
            add_category_goal_form = AddCategoryGoalForm(user=user)
        if edit_category_goal_form is None:
            edit_category_goal_form = EditCategoryGoalForm(user=user)


    # Handle get requests, show new forms
    else:
        # Empty add account goal form
        add_account_goal_form = AddAccountGoalForm(user=user)
        add_category_goal_form = AddCategoryGoalForm(user=user)
        if editing_goal:
            # Load the right form depending on the goal type
            if form_type == "edit-acct-goal":
                edit_account_goal_form = EditAccountGoalForm(instance=editing_goal, user=user)
                edit_category_goal_form = EditCategoryGoalForm(user=user)
                acct_goal_edit = True
            elif form_type == "edit-cat-goal":
                edit_category_goal_form = EditCategoryGoalForm(instance=editing_goal, user=user)
                edit_account_goal_form = EditAccountGoalForm(user=user)
                cat_goal_edit = True
        else:
            edit_account_goal_form = EditAccountGoalForm(user=user)
            edit_category_goal_form = EditCategoryGoalForm(user=user)

    # Get list of account goals to give to the template
    acct_goals = AccountGoal.objects.filter(user=user)
    if acct_goals.exists():
        # Only show goals that aren't expired
        cur_acct_goals = [goal for goal in acct_goals if goal.is_current()]
    else:
        cur_acct_goals = None

    # Get a list of the user's categories to choose from to view its goals
    user_cats = Category.objects.filter(user=user)
    # Get a list of all the user's goals in all the categories
    cat_goals = CategoryGoal.objects.filter(category__user=user)
    # Only show current cat goals
    cur_cat_goals = [goal for goal in cat_goals if goal.is_current()]


    return render(request, "finances/goals.html", context={
        "cur_acct_goals": cur_acct_goals,
        "user_cats": user_cats,
        "cur_cat_goals": cur_cat_goals,
        "add_account_goal_form": add_account_goal_form,
        "edit_account_goal_form": edit_account_goal_form,
        "add_category_goal_form": add_category_goal_form,
        "edit_category_goal_form": edit_category_goal_form,
        "acct_goal_add": acct_goal_add,
        "acct_goal_edit": acct_goal_edit,
        "cat_goal_add": cat_goal_add,
        "cat_goal_edit": cat_goal_edit,
        })


@require_POST
def delete_goals(request):
    # Needs category goals
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not authenticated"}, status=401)
    data = json.loads(request.body)
    
    # Delete account goals
    acct_goal_ids = data.get("acctGoals", [])
    if acct_goal_ids:
        acct_goals = AccountGoal.objects.filter(user=request.user, id__in=acct_goal_ids)
        acct_goals.delete()
    
    # Delete category goals
    cat_goal_ids = data.get("catGoals", [])
    if cat_goal_ids:
        cat_goals = CategoryGoal.objects.filter(category__user=request.user, id__in=cat_goal_ids)
        cat_goals.delete()

    return JsonResponse({'success': True})

