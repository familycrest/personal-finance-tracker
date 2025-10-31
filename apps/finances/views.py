from datetime import datetime, date, timedelta
from calendar import monthrange

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST
from django.contrib import messages
from django.http import JsonResponse
import json

from django.utils import timezone

from .models import Entry, Category, EntryType, AccountGoal, CategoryGoal
from .forms import CategoryForm, EntryForm, EntryFilterForm, AddAccountGoalForm, EditAccountGoalForm

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
    # TODO: make this mess comprehensible!! maybe split into editing and non-editing branches, at the cost of violating DRY

    # Default form
    entry_form = EntryForm(initial={
        "date": datetime.today().strftime("%Y-%m-%d"), # IDK if this is required by something else, but the format should be month/day/year.
        "entry_type": EntryType.EXPENSE,
    })
    
    editing = False

    if request.GET.get("edit"):
        edit_id = request.GET.get("edit")

        try:
            entry = Entry.objects.get(pk=edit_id)
            entry_form = EntryForm(instance=entry)
            editing = True
        except:
            entry_form.add_error(error=f"Could not find transaction {edit_id}")

    # Handle form submissions
    if request.method == "POST": 
        if editing:
            entry_form = EntryForm(request.POST, instance=entry)
        else:
            entry_form = EntryForm(request.POST)

        if entry_form.is_valid():
            if editing:
                entry_form = entry_form.save(commit=False)
                entry_form.user = request.user
                entry_form.save()

                return redirect("transactions")
            else:
                # Create a new entry from the form, without saving it to the server yet
                new_entry = entry_form.save(commit=False)
                
                # Assign this entry to the current user and finally save it
                new_entry.user = request.user
                new_entry.save()

                return redirect("transactions")

    # TODO: maybe encapsulate this in its own function
    # display the transaction and category entered by user
    categories = Category.objects.filter(user=request.user)
    user_entries = Entry.objects.filter(user=request.user).order_by("-date")
    entries_output = user_entries

    # Big big big big big big thanks to https://stackoverflow.com/a/43096716/8746360
    # A bound form (one with the request given to it) does not have initial values
    if request.GET and EntryFilterForm.base_fields.keys(): # This used to be &, maybe it should still be. IDK.
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
        "add_form_data": {},  # avoid template errors
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


@login_required
def goals(request):
    """
    View for CRUD operations for AccountGoals and CategoryGoals.
    """
    # Whether each dialog is visible on page load, in case of form error
    acct_goal_add = False
    acct_goal_edit = False

    user = request.user
    # Goal being edited
    editing_goal = None
    # TODO: add category goals

    # Check if we're editing via query parameter edit
    edit_id = request.GET.get("edit")
    if edit_id:
        try:
            editing_goal = AccountGoal.objects.get(pk=edit_id, user=user)
        except AccountGoal.DoesNotExist:
            return redirect("goals")
    
    # Handle post requests, accept forms to add a new goal or edit an existing goal
    if request.method == "POST":
        form_type = request.POST.get("form_type")

        if form_type == "edit" and editing_goal:
            # Edit existing goal
            edit_account_goal_form = EditAccountGoalForm(request.POST, instance=editing_goal, user=user)
            if edit_account_goal_form.is_valid():
                edit_account_goal_form.save()
                return redirect("goals")
            else:
                # Open the edit dialog upon next page render to see errors
                acct_goal_edit = True
            # Have add account goal form loaded (not open) on page just in case
            add_account_goal_form = AddAccountGoalForm(user=user)
        
        else:
            # Add new goal
            add_account_goal_form = AddAccountGoalForm(request.POST, user=user)
            if add_account_goal_form.is_valid():
                add_account_goal_form.save()
                return redirect("goals")
            else:
                # Open the add dialog next page render to see errors
                acct_goal_add = True
            # Have edit account goal form loaded (not open) just in case
            edit_account_goal_form = EditAccountGoalForm(user=user)

    # Handle get requests, show new forms
    else:
        # Empty add account goal form
        add_account_goal_form = AddAccountGoalForm(user=user)
        if editing_goal:
            # Edit existing goal
            edit_account_goal_form = EditAccountGoalForm(instance=editing_goal, user=user)
            acct_goal_edit = True
        else:
            # Empty form just to have it existing in the background
            edit_account_goal_form = EditAccountGoalForm(user=user)

    # Get list of account goals to give to the template
    acct_goals = user.get_account_goals()
    if acct_goals:
        # Only show goals that aren't expired
        cur_acct_goals = [goal for goal in acct_goals if goal.is_current()]
    else:
        cur_acct_goals = None

    # Get a list of the user's goals to use as options for goal sorting
    user_cats = Category.objects.filter(user=user)
    # Get a list of all the goals in all the categories
    cat_goals = [goal for cat in user_cats for goal in cat.get_goals()]
    # Only show current cat goals
    cur_cat_goals = [goal for goal in cat_goals if goal.is_current()]


    return render(request, "finances/goals.html", context={
        "cur_acct_goals": cur_acct_goals,
        "user_cats": user_cats,
        "cur_cat_goals": cur_cat_goals,
        "add_account_goal_form": add_account_goal_form,
        "edit_account_goal_form": edit_account_goal_form,
        "acct_goal_add": acct_goal_add,
        "acct_goal_edit": acct_goal_edit,
        })



@require_POST
def delete_goals(request):
    # Needs category goals
    if not request.user.is_authenticated:
        return JsonResponse({"error": "not authenticated"}, 401)
    data = json.loads(request.body)
    goal_ids = data.get('acctGoals')
    goals = AccountGoal.objects.filter(user=request.user, id__in=goal_ids)
    
    goals.delete()

    return JsonResponse({'success': True})
