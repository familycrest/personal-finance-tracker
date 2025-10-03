from .forms import CustomUserCreationForm
from django.contrib.auth import login, get_user_model
from django.shortcuts import render, redirect

def signup(request):
    print("i just received a request!")

    # Redirect the user to the dashboard if they're already logged in
    if request.user.is_authenticated:
        print("the user is already logged in though, so no need for them to sign up. sending them to their dashboard!")

        return redirect("dashboard")
    
    user = get_user_model()
    if request.method == "POST":
        
        print("request is a POST, so that means that it's a form submission!")

        form = CustomUserCreationForm(request.POST)

        if form.is_valid():
            print("yay, the form is valid!")

            user = form.save()  # save the new user
            login(request, user)  # log the user in automatically
            return redirect("dashboard")  # redirect to dashboard
        else:
            print("unfortunately, the form was invalid :( telling the user now")
            
            return redirect("")

    else:

        form = CustomUserCreationForm()
    return render(request, "accounts/signup.html", {"form": form})
