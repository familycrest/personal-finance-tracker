from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import login
from django.shortcuts import render, redirect

def signup(request):
    if request.method == "POST":
        form = UserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()        # save the new user
            login(request, user)      # log the user in automatically
            return redirect("dashboard")  # redirect to dashboard
    else:
        form = UserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})
