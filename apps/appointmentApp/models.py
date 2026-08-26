from django.db import models
from django.utils import timezone

from apps.userApp.models import CustomUser
from apps.doctorApp.models import DoctorProfile
from apps.hospitalApp.models import Hospital


# Appointment Status Choices
APPOINTMENT_STATUS_CHOICES = (
    ("pending", "Pending"),
    ("approved", "Approved"),
    ("cancelled", "Cancelled"),
    ("completed", "Completed"),
)

# Days Choices
DAYS_CHOICES = (
    ("saturday", "Saturday"),
    ("sunday", "Sunday"),
    ("monday", "Monday"),
    ("tuesday", "Tuesday"),
    ("wednesDay", "WednesDay"),
    ("thursday", "Thursday"),
    ("friday", "Friday"),
)


# --- APPOINTMENTS TABLE ---


class Appointment(models.Model):
    # Relationship (FK -> Users: Patient)
    patient = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="appointments_as_patient",
        limit_choices_to={"role": "patient"},
    )

    # Relationship (FK -> Hospitals)
    hospital = models.ForeignKey(
        Hospital, on_delete=models.PROTECT, related_name="appointments"
    )

    # Relationship (FK -> DoctorProfile)
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.PROTECT, related_name="appointments"
    )

    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    status = models.CharField(
        max_length=20, choices=APPOINTMENT_STATUS_CHOICES, default="pending"
    )

    # Relationship (FK -> Users: Patient or Staff)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="appointments_created",
        help_text="User (Patient, Staff, or Admin) who booked the appointment.",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["appointment_date", "appointment_time"]

    def __str__(self):

        return f"Appointment for {self.patient.full_name} with {self.doctor.user.full_name} on {self.appointment_date}"
