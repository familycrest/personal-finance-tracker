# finances/views.py

from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from .models import Entry, Category, EntryType, AccountGoal  # this line imports the models from finance/models.py
from django.utils import timezone

# Create your views here.
@login_required
def input_transaction(request):
    if request.method == "POST":
        date = request.POST.get("date")
        name = request.POST.get("name")
        amount = request.POST.get("amount")
        entry_type = request.POST.get("entry_type")
        category_id = request.POST.get("category")
        description = request.POST.get("description", "")
        account_goal_id = request.POST.get("account_goal")

        # make sure all data items are given by user before saving
        if date and name and amount:
            category = Category.objects.get(id=category_id) if category_id else None
            goal = Goal.objects.get(id=goal_id) if goal_id else None

            # create the entries by the user
            Entry.objects.create(
                user=request.user,
                date=date,
                name=name,
                amount=amount,
                entry_type=entry_type,
                category=category,
                description=description,
                goal=account_goal,
            )
            return redirect("output_transactions")

    categories = Category.objects.filter(user=request.user)
    account_goals = AccountGoal.objects.filter(user=request.user)
    context = {
        "categories": categories,
        "account_goals": account_goals,
        "entry_types": EntryType.choices,
    }
    return render(request, "finances/input_transaction.html", context)


# create view for output of transaction entries
@login_required
def output_transaction(request):
    transactions = Entry.objects.filter(user=request.user).order_by("-date")
    return render(request, "finances/output_transactions.html", {"transactions": transactions})
