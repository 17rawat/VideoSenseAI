from django.shortcuts import render, redirect
from django.contrib.auth.models import User
from django.contrib.auth import login, logout, authenticate


def user_login(request):
    if request.method == "POST":
        username = request.POST["username"]
        password = request.POST["password"]

        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect("/analyze")

        else:
            error_message = "Invaild username or password"
            return render(
                request, "account/login.html", {"error_message": error_message}
            )

    return render(request, "account/login.html")


def user_signup(request):
    if request.method == "POST":
        username = request.POST["username"]
        email = request.POST["email"]
        password = request.POST["password"]

        if User.objects.filter(username=username).exists():
            error_message = "Username already taken"
            return render(
                request, "account/signup.html", {"error_message": error_message}
            )

        elif User.objects.filter(email=email).exists():
            error_message = "Email already registered"
            return render(
                request, "account/signup.html", {"error_message": error_message}
            )

        else:
            try:
                user = User.objects.create_user(username, email, password)
                user.save()
                login(request, user)
                return redirect("/analyze")

            except:  # noqa: E722
                error_message = "Error while creating account"
                return render(
                    request, "account/signup.html", {"error_message": error_message}
                )

    return render(request, "account/signup.html")


def user_logout(request):
    logout(request)
    return redirect("/")
