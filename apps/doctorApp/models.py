from django.core.validators import MaxValueValidator, MinValueValidator
from django.db import models
from django.utils import timezone

from apps.userApp.models import CustomUser
from apps.hospitalApp.models import Hospital


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


class DoctorSpecialized(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Specilized in.")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.name}"


class DoctorProfile(models.Model):
    # Relationship (FK -> Users: Doctor)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name="doctor_profile",
        limit_choices_to={
            "role": "doctor"
        },  # Ensures only 'doctor' users get a profile
    )

    # Relationship (M-2-M -> Hospitals)
    hospital = models.ManyToManyField(
        Hospital,
        related_name="doctors",
        help_text="One doctor can belongs to multiple hospitals.",
    )

    specialized = models.ManyToManyField(DoctorSpecialized, related_name="doctors")

    image = models.URLField(blank=True, null=True)
    chamber_room = models.CharField(max_length=50, blank=True, null=True)  # Optional
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    search_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)

    def get_full_name(self):
        return self.user.full_name

    def get_hospital_name(self):
        return f"{', '.join([h.name for h in self.hospital.all()])}"

    def __str__(self):
        return f"Dr. {self.user.full_name}"

    class Meta:
        verbose_name = "Doctor Profile"
        verbose_name_plural = "Doctor Profiles"


class DoctorSchedule(models.Model):
    # Relationship (FK -> DoctorProfile)
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="schedules"
    )
    days = models.CharField(
        max_length=20,
        choices=DAYS_CHOICES,
        default="saturday",
        help_text="Day of the week.",
    )
    # available_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(
        help_text="Duration in minutes for each appointment slot (e.g., 15)."
    )

    # Relationship (FK -> Users: Staff or Admin)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name="schedules_created",
        limit_choices_to=models.Q(role="hospital_admin") | models.Q(role="staff"),
        help_text="User (Hospital Admin or Staff) who created the schedule.",
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ("doctor", "days", "start_time")
        ordering = ["days", "start_time"]

    def __str__(self):
        return f"{self.doctor.user.full_name} on {self.days}"


class DoctorQualification(models.Model):
    # Relationship (FK -> DoctorProfile)
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="qualification"
    )
    name = models.CharField(max_length=150, help_text="Qualification Title.")
    institution = models.CharField(max_length=150, help_text="Institution Name.")
    passing_year = models.PositiveIntegerField(help_text="Year of Passing.")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["name"]

    def __str__(self):
        return f"{self.doctor.user.full_name}"


class DoctorReview(models.Model):
    doctor = models.ForeignKey(
        DoctorProfile, on_delete=models.CASCADE, related_name="reviews"
    )
    user = models.ForeignKey(
        CustomUser, on_delete=models.CASCADE, related_name="doctor_reviews"
    )
    rating = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)],
        help_text="Rating from 1 to 5 stars.",
    )
    comment = models.TextField(blank=True, null=True)
    show = models.BooleanField(
        default=True, help_text="Control review visibility on the platform."
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ["-created_at"]
        unique_together = (
            "doctor",
            "user",
        )  # Prevents duplicate reviews from the same user

    def __str__(self):
        return f"Review by {self.user.full_name} for Dr. {self.doctor.user.full_name} ({self.rating}★)"
