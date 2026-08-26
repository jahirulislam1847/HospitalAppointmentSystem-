from django.urls import path
from .views import (
    create_appointment,
    get_available_slots_ajax,
    get_schedule_dates_ajax,
    AppointmentDetailView,
)

app_name = "appointmentApp"

urlpatterns = [
    path("book/<int:doctor_id>/", create_appointment, name="create_appointment"),
    path("<int:pk>/", AppointmentDetailView.as_view(), name="appointment_detail"),
    path(
        "ajax/get-schedule-dates/",
        get_schedule_dates_ajax,
        name="ajax_get_schedule_dates",
    ),
    path(
        "ajax/get-available-slots/",
        get_available_slots_ajax,
        name="ajax_get_available_slots",
    ),
]
