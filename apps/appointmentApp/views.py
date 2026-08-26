from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from datetime import datetime, timedelta
from django.views.generic import DetailView
from django.contrib.auth.mixins import LoginRequiredMixin

from apps.doctorApp.models import DoctorProfile, DoctorSchedule
from .models import Appointment
from .forms import AppointmentBookingForm, DAY_MAP


@login_required
def create_appointment(request, doctor_id):
    doctor = get_object_or_404(DoctorProfile, pk=doctor_id)

    if request.method == "POST":
        form = AppointmentBookingForm(request.POST, doctor=doctor)
        if form.is_valid():
            appointment_time_str = form.cleaned_data["appointment_time"]
            target_date_str = form.cleaned_data["target_date"]

            target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
            time_obj = datetime.strptime(appointment_time_str, "%H:%M:%S").time()

            # Prevent double booking race condition for the chosen date & time
            if (
                Appointment.objects.filter(
                    doctor=doctor,
                    appointment_date=target_date,
                    appointment_time=time_obj,
                )
                .exclude(status="cancelled")
                .exists()
            ):
                messages.error(
                    request,
                    "This slot was just booked by someone else. Please choose another slot.",
                )
            else:
                appointment = form.save(commit=False)
                appointment.patient = request.user
                appointment.doctor = doctor
                appointment.appointment_date = target_date
                appointment.appointment_time = time_obj
                appointment.created_by = request.user
                appointment.status = "pending"
                appointment.save()

                messages.success(request, "Appointment booked successfully!")
                return redirect("appointmentApp:appointment_detail", pk=appointment.pk)
    else:
        form = AppointmentBookingForm(doctor=doctor)

    return render(
        request,
        "appointmentApp/create_appointment.html",
        {
            "form": form,
            "doctor": doctor,
        },
    )


def get_schedule_dates_ajax(request):
    """Calculates upcoming dates for the next 2 weeks matching the schedule's `days` field."""
    schedule_id = request.GET.get("schedule_id")
    if not schedule_id:
        return JsonResponse({"dates": []})

    try:
        schedule = DoctorSchedule.objects.get(pk=schedule_id)
    except DoctorSchedule.DoesNotExist:
        return JsonResponse({"dates": []})

    today = datetime.now().date()
    dates = []

    # Access `schedule.days` and lower-case it to match DAY_MAP
    raw_day = str(schedule.days).strip().lower()
    target_weekday = DAY_MAP.get(raw_day, 0)

    for i in range(14):
        check_date = today + timedelta(days=i)
        if check_date.weekday() == target_weekday:
            dates.append(
                {
                    "value": check_date.strftime("%Y-%m-%d"),
                    "display": check_date.strftime("%A, %b %d, %Y"),
                }
            )

    return JsonResponse({"dates": dates})


def get_available_slots_ajax(request):
    """Fetches time slots for a schedule and filters out appointments booked on the selected date."""
    schedule_id = request.GET.get("schedule_id")
    target_date_str = request.GET.get("date")

    if not schedule_id or not target_date_str:
        return JsonResponse({"slots": []})

    try:
        schedule = DoctorSchedule.objects.get(pk=schedule_id)
        target_date = datetime.strptime(target_date_str, "%Y-%m-%d").date()
    except (DoctorSchedule.DoesNotExist, ValueError):
        return JsonResponse({"slots": []})

    curr_time = datetime.combine(target_date, schedule.start_time)
    end_dt = datetime.combine(target_date, schedule.end_time)
    slot_delta = timedelta(minutes=schedule.slot_duration)

    # Exclude times already booked on this exact target date
    booked_times = set(
        Appointment.objects.filter(doctor=schedule.doctor, appointment_date=target_date)
        .exclude(status="cancelled")
        .values_list("appointment_time", flat=True)
    )

    available_slots = []
    while curr_time + slot_delta <= end_dt:
        if curr_time.time() not in booked_times:
            available_slots.append(
                {
                    "value": curr_time.time().strftime("%H:%M:%S"),
                    "display": curr_time.time().strftime("%I:%M %p"),
                }
            )
        curr_time += slot_delta

    return JsonResponse({"slots": available_slots})


class AppointmentDetailView(LoginRequiredMixin, DetailView):
    model = Appointment
    template_name = "appointmentApp/appointment_detail.html"
    context_object_name = "appointment"
    pk_url_kwarg = "pk"

    def get_queryset(self):
        user = self.request.user
        # Restrict patients to viewing only their own appointments
        if user.role == "patient":
            qs = Appointment.objects.filter(patient=user)
        elif user.role == "doctor":
            qs = Appointment.objects.filter(doctor__user=user)
        elif user.role in ["hospital_admin", "staff"]:
            qs = Appointment.objects.filter(hospital__in=user.hospital.all())
        else:  # super_admin
            qs = Appointment.objects.all()
        return qs.select_related("doctor__user", "hospital", "patient")
