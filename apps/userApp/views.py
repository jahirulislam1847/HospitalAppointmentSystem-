from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from .forms import RegisterForm, EmailAuthenticationForm


def register_view(request):
    if request.user.is_authenticated:
        return redirect("userApp:dashboard")

    if request.method == "POST":
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = form.cleaned_data["email"]
            user.role = "patient"  # self-registration is always a patient account
            user.set_password(form.cleaned_data["password"])
            user.save()

            login(request, user)
            messages.success(request, f"Welcome, {user.full_name}! Your account has been created.")
            return redirect("userApp:dashboard")
    else:
        form = RegisterForm()

    return render(request, "userApp/register.html", {"form": form})


class CustomLoginView(LoginView):
    template_name = "userApp/login.html"
    authentication_form = EmailAuthenticationForm
    redirect_authenticated_user = True

    def form_valid(self, form):
        response = super().form_valid(form)
        messages.success(self.request, f"Welcome back, {self.request.user.full_name}!")
        return response

    def get_success_url(self):
        return str(reverse_lazy("userApp:dashboard"))


@require_POST
def logout_view(request):
    logout(request)
    messages.info(request, "You have been logged out successfully.")
    return redirect("userApp:login")


@login_required(login_url="userApp:login")
def dashboard_view(request):
    # Placeholder landing page post-login. Will branch per role once
    # hospital/doctor/patient/appointment endpoints are provided.
    return render(request, "userApp/profile/dashboard.html")