from .forms import CustomUserCreationForm
from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect

def signup(request):
    # Redirect the user to the dashboard if they're already logged in
    if request.user.is_authenticated:
        return redirect("dashboard")
    
    user = get_user_model()
    if request.method == "POST":
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            user = form.save()  # save the new user
            login(request, user)  # log the user in automatically
            return redirect("dashboard")  # redirect to dashboard
    else:
        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})
