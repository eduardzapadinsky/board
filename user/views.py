from django.contrib.auth.views import LogoutView
from django.shortcuts import render, redirect
from django.contrib import auth
from django.contrib import messages
from rest_framework import viewsets

from .models import UserModel
from .forms import RegistrationForm, LoginForm
from .serializers import UserSerializer


class UserViewAPI(viewsets.ModelViewSet):
    queryset = UserModel.objects.all()
    serializer_class = UserSerializer


def register(request):
    """
    Register user and login if successful

    """
    if request.method == "POST":
        form = RegistrationForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = UserModel.objects.create_user(
                username=cd["username"],
                first_name=cd["first_name"],
                email=cd["email"],
                password=cd["password"]
            )
            user.save()

            if user:
                auth.login(request, user)
                user.is_active = True
                user.save()
                return redirect("dashboard:board")
        else:
            messages.warning(request, "Fill in the fields correctly")

    form = RegistrationForm()
    context = {
        "form": form
    }
    return render(request, "user/register.html", context=context)


def login(request):
    """
    Login user
    """
    if request.method == "POST":
        form = LoginForm(request.POST)
        if form.is_valid():
            cd = form.cleaned_data
            user = auth.authenticate(username=cd["username"], password=cd["password"])
            if user:
                auth.login(request, user)
                user.is_active = True
                user.save()
            else:
                messages.warning(request, "Check your name and password")
                return render(request, "user/login.html", {"form": form})
            return redirect("dashboard:board")
    else:
        form = LoginForm()
    return render(request, "user/login.html", {"form": form})


class Logout(LogoutView):
    """
    Logout user
    """
    next_page = "dashboard:board"
