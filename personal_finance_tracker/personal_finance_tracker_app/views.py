# personal_finance_tracker_app/views.py
# Create your views here.
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from .forms import TransactionForm
from .models import Transaction


def home(request):
    return render(request, "personal_finance_tracker_app/home.html")


@login_required
def dashboard(request):
    return render(request, "personal_finance_tracker_app/dashboard.html")


def transactions(request):
    if request.method == "POST":
        form = TransactionForm(request.POST)
        if form.is_valid():
            form.save()
            # create a redirect to see the list of transactions created
            return redirect("transactions_list")
    else:
        form = TransactionForm()
    return render(request, "personal_finance_tracker_app/transactions.html", {"form": form})  # this is needed to pass the form back to transactions.html. Won't work without it.

def transactions_list(request):
    # pass information from transactions to list
    transactions_listed = Transaction.objects.filter(user=request.user).order_by("-date")
    return render(request, "personal_finance_tracker_app/transactions_list.html", {"transactions": transactions_listed})

def reports(request):
    return render(request, "personal_finance_tracker_app/reports.html")
