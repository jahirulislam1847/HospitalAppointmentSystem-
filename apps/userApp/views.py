from django.contrib import messages
from django.contrib.auth import login, logout
from django.contrib.auth.decorators import login_required
from django.contrib.auth.views import LoginView
from django.shortcuts import render, redirect
from django.urls import reverse_lazy
from django.views.decorators.http import require_POST

from apps.appointmentApp.models import Appointment
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
            messages.success(
                request, f"Welcome, {user.full_name}! Your account has been created."
            )
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
    current_url = request.resolver_match.url_name
    user = request.user

    # Base context available across dashboard sub-views
    context = {
        'current_tab': current_url,
    }

    # Fetch role-based appointments
    if user.role == 'patient':
        appointments_qs = Appointment.objects.filter(patient=user)
    elif user.role == 'doctor':
        appointments_qs = Appointment.objects.filter(doctor__user=user)
    elif user.role in ['hospital_admin', 'staff']:
        appointments_qs = Appointment.objects.filter(hospital__in=user.hospital.all())
    else:  # super_admin
        appointments_qs = Appointment.objects.all()

    appointments_qs = appointments_qs.select_related(
        'doctor__user', 'patient', 'hospital'
    ).order_by('-id')

    # 1. Profile Tab
    if current_url == 'dashboard_profile':
        if request.method == 'POST':
            full_name = request.POST.get('full_name', '').strip()
            phone = request.POST.get('phone', '').strip()

            if full_name:
                user.full_name = full_name
                user.phone = phone
                user.save()
                messages.success(request, "Profile updated successfully.")
                return redirect('userApp:dashboard_profile')
            else:
                messages.error(request, "Full name cannot be empty.")

        context.update({'section': 'profile'})

    # 2. Appointment List Tab
    elif current_url == 'dashboard_appointment_list':
        context.update({
            'section': 'appointment_list',
            'appointments': appointments_qs,
        })

    # 3. Dashboard Overview Tab (Default)
    else:
        context.update({
            'section': 'overview',
            'appointments_count': appointments_qs.count(),
            'pending_count': appointments_qs.filter(status='pending').count(),
            'approved_count': appointments_qs.filter(status='approved').count(),
            'recent_appointments': appointments_qs[:5],
        })

    return render(request, "userApp/profile/dashboard.html", context)
