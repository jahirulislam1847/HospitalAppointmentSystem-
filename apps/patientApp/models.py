from django.db import models
from django.utils import timezone

from apps.userApp.models import CustomUser


# Gender Choices (for PatientProfile)
GENDER_CHOICES = (
    ('male', 'Male'),
    ('female', 'Female'),
    ('other', 'Other'),
)



class PatientProfile(models.Model):
    # Relationship (FK -> Users: Patient)
    user = models.OneToOneField(
        CustomUser,
        on_delete=models.CASCADE,
        primary_key=True,
        related_name='patient_profile',
        limit_choices_to={'role': 'patient'} # Ensures only 'patient' users get a profile
    )

    image = models.URLField(blank=True, null=True)
    dob = models.DateField(null=True, blank=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
    address = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return self.user.full_name

    class Meta:
        verbose_name = 'Patient Profile'
        verbose_name_plural = 'Patient Profiles'

