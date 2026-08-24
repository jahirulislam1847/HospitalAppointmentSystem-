from django.db import models
from django.utils import timezone

from apps.userApp.models import CustomUser
from apps.hospitalApp.models import Hospital


# Days Choices
DAYS_CHOICES = (
    ('saturday', 'Saturday'),
    ('sunday', 'Sunday'),
    ('monday', 'Monday'),
    ('tuesday', 'Tuesday'),
    ('wednesDay', 'WednesDay'),
    ('thursday', 'Thursday'),
    ('friday', 'Friday'),
)



class DoctorSpecialized(models.Model):
    name = models.CharField(max_length=150, unique=True, help_text="Specilized in.")
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.name}"


class DoctorProfile(models.Model):
    # Relationship (FK -> Users: Doctor)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='doctor_profile',
        limit_choices_to={'role': 'doctor'} # Ensures only 'doctor' users get a profile
    )

    # Relationship (FK -> Hospitals)
    hospital = models.ForeignKey(
        Hospital,
        on_delete=models.CASCADE,
        related_name='doctors'
    )
    
    specialized = models.ManyToManyField(
        DoctorSpecialized,
        related_name='doctors'
    )

    image = models.URLField(blank=True, null=True)
    chamber_room = models.CharField(max_length=50, blank=True, null=True) # Optional
    fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    search_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(default=timezone.now)
    
    def get_full_name(self):
        return self.user.full_name
    
    def get_hospital_name(self):
        return self.hospital.name

    def __str__(self):
        return f"Dr. {self.user.full_name}"
    
    
    class Meta:
        verbose_name = 'Doctor Profile'
        verbose_name_plural = 'Doctor Profiles'


class DoctorSchedule(models.Model):
    # Relationship (FK -> DoctorProfile)
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='schedules'
    )
    days = models.CharField(max_length=20, choices=DAYS_CHOICES, default='saturday', help_text="Day of the week.")
    available_date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    slot_duration = models.IntegerField(help_text="Duration in minutes for each appointment slot (e.g., 15).")

    # Relationship (FK -> Users: Staff or Admin)
    created_by = models.ForeignKey(
        CustomUser,
        on_delete=models.PROTECT,
        related_name='schedules_created',
        limit_choices_to=models.Q(role='hospital_admin') | models.Q(role='staff'),
        help_text="User (Hospital Admin or Staff) who created the schedule."
    )
    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        unique_together = ('doctor', 'days', 'available_date', 'start_time')
        ordering = ['days', 'available_date', 'start_time']

    def __str__(self):
        return f"{self.doctor.user.full_name} on {self.days} - {self.available_date}"



class DoctorQualification(models.Model):
    # Relationship (FK -> DoctorProfile)
    doctor = models.ForeignKey(
        DoctorProfile,
        on_delete=models.CASCADE,
        related_name='qualification'
    )
    name = models.CharField(max_length=150, unique=True, help_text="Qualification Title.")
    institution = models.CharField(max_length=150, help_text="Institution Name.")
    passing_year = models.PositiveIntegerField(help_text="Year of Passing.")

    created_at = models.DateTimeField(default=timezone.now)

    class Meta:
        ordering = ['name']

    def __str__(self):
        return f"{self.doctor.user.full_name}"

