# from django.db import models
# from django.utils import timezone

# from apps.userApp.models import CustomUser
# from apps.doctorApp.models import DoctorProfile
# from apps.hospitalApp.models import Hospital


# # Appointment Status Choices
# APPOINTMENT_STATUS_CHOICES = (
#     ('pending', 'Pending'),
#     ('approved', 'Approved'),
#     ('cancelled', 'Cancelled'),
#     ('completed', 'Completed'),
# )

# # Days Choices
# DAYS_CHOICES = (
#     ('saturday', 'Saturday'),
#     ('sunday', 'Sunday'),
#     ('monday', 'Monday'),
#     ('tuesday', 'Tuesday'),
#     ('wednesDay', 'WednesDay'),
#     ('thursday', 'Thursday'),
#     ('friday', 'Friday'),
# )


# # --- APPOINTMENTS TABLE ---

# class Appointment(models.Model):
#     # Relationship (FK -> Users: Patient)
#     patient = models.ForeignKey(
#         CustomUser,
#         on_delete=models.PROTECT,
#         related_name='appointments_as_patient',
#         limit_choices_to={'role': 'patient'}
#     )

#     # Relationship (FK -> Hospitals)
#     hospital = models.ForeignKey(
#         Hospital,
#         on_delete=models.PROTECT,
#         related_name='appointments'
#     )

#     # Relationship (FK -> DoctorProfile)
#     doctor = models.ForeignKey(
#         DoctorProfile,
#         on_delete=models.PROTECT,
#         related_name='appointments'
#     )

#     appointment_date = models.DateField()
#     appointment_time = models.TimeField()
#     status = models.CharField(
#         max_length=20,
#         choices=APPOINTMENT_STATUS_CHOICES,
#         default='pending'
#     )

#     # Relationship (FK -> Users: Patient or Staff)
#     created_by = models.ForeignKey(
#         CustomUser,
#         on_delete=models.PROTECT,
#         related_name='appointments_created',
#         help_text="User (Patient, Staff, or Admin) who booked the appointment."
#     )
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ['appointment_date', 'appointment_time']

#     def __str__(self):
        
#         return f"Appointment for {self.patient.full_name} with {self.doctor.user.full_name} on {self.appointment_date}"


# from django.db import models
# from django.utils import timezone

# from apps.userApp.models import CustomUser
# from apps.hospitalApp.models import Hospital


# # Days Choices
# DAYS_CHOICES = (
#     ('saturday', 'Saturday'),
#     ('sunday', 'Sunday'),
#     ('monday', 'Monday'),
#     ('tuesday', 'Tuesday'),
#     ('wednesDay', 'WednesDay'),
#     ('thursday', 'Thursday'),
#     ('friday', 'Friday'),
# )



# class DoctorSpecialized(models.Model):
#     name = models.CharField(max_length=150, unique=True, help_text="Specilized in.")
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ['name']

#     def __str__(self):
#         return f"{self.name}"


# class DoctorProfile(models.Model):
#     # Relationship (FK -> Users: Doctor)
#     user = models.OneToOneField(
#         CustomUser,
#         on_delete=models.CASCADE,
#         primary_key=True,
#         related_name='doctor_profile',
#         limit_choices_to={'role': 'doctor'} # Ensures only 'doctor' users get a profile
#     )

#     # Relationship (FK -> Hospitals)
#     hospital = models.ForeignKey(
#         Hospital,
#         on_delete=models.CASCADE,
#         related_name='doctors'
#     )
    
#     specialized = models.ManyToManyField(
#         DoctorSpecialized,
#         related_name='doctors'
#     )

#     image = models.URLField(blank=True, null=True)
#     chamber_room = models.CharField(max_length=50, blank=True, null=True) # Optional
#     fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
#     search_count = models.PositiveIntegerField(default=0)
#     created_at = models.DateTimeField(default=timezone.now)
    
#     def get_full_name(self):
#         return self.user.full_name
    
#     def get_hospital_name(self):
#         return self.hospital.name

#     def __str__(self):
#         return f"Dr. {self.user.full_name}"
    
    
#     class Meta:
#         verbose_name = 'Doctor Profile'
#         verbose_name_plural = 'Doctor Profiles'


# class DoctorSchedule(models.Model):
#     # Relationship (FK -> DoctorProfile)
#     doctor = models.ForeignKey(
#         DoctorProfile,
#         on_delete=models.CASCADE,
#         related_name='schedules'
#     )
#     days = models.CharField(max_length=20, choices=DAYS_CHOICES, default='saturday', help_text="Day of the week.")
#     available_date = models.DateField()
#     start_time = models.TimeField()
#     end_time = models.TimeField()
#     slot_duration = models.IntegerField(help_text="Duration in minutes for each appointment slot (e.g., 15).")

#     # Relationship (FK -> Users: Staff or Admin)
#     created_by = models.ForeignKey(
#         CustomUser,
#         on_delete=models.PROTECT,
#         related_name='schedules_created',
#         limit_choices_to=models.Q(role='hospital_admin') | models.Q(role='staff'),
#         help_text="User (Hospital Admin or Staff) who created the schedule."
#     )
#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         unique_together = ('doctor', 'days', 'available_date', 'start_time')
#         ordering = ['days', 'available_date', 'start_time']

#     def __str__(self):
#         return f"{self.doctor.user.full_name} on {self.days} - {self.available_date}"



# class DoctorQualification(models.Model):
#     # Relationship (FK -> DoctorProfile)
#     doctor = models.ForeignKey(
#         DoctorProfile,
#         on_delete=models.CASCADE,
#         related_name='qualification'
#     )
#     name = models.CharField(max_length=150, unique=True, help_text="Qualification Title.")
#     institution = models.CharField(max_length=150, help_text="Institution Name.")
#     passing_year = models.PositiveIntegerField(help_text="Year of Passing.")

#     created_at = models.DateTimeField(default=timezone.now)

#     class Meta:
#         ordering = ['name']

#     def __str__(self):
#         return f"{self.doctor.user.full_name}"

# from django.db import models
# from django.utils import timezone
# from django.utils.text import slugify


# class Hospital(models.Model):
#     name = models.CharField(max_length=255)
#     slug = models.SlugField(unique=True, blank=True)
#     address = models.TextField()
#     contact = models.CharField(max_length=20)
#     email = models.EmailField()
#     image = models.URLField(blank=True, null=True)
#     search_count = models.PositiveIntegerField(default=0)

#     # Relationship (FK -> Users: Super Admin)
#     created_by = models.ForeignKey(
#         'userApp.CustomUser',
#         on_delete=models.PROTECT, # Protects the hospital record from deletion if the creator is still needed
#         related_name='hospitals_created',
#         limit_choices_to={'role': 'super_admin'} # Only super admins can create hospitals
#     )
#     created_at = models.DateTimeField(default=timezone.now)
    
#     def save(self, *args, **kwargs):
#         # Only set slug if not provided manually
#         if not self.slug:
#             base_slug = slugify(self.name)
#             self.slug = base_slug
#         super().save(*args, **kwargs)

#     def __str__(self):
#         return self.name
    
#     class Meta:
#         verbose_name = 'Hospital'
#         verbose_name_plural = 'Hospitals'

# from django.db import models
# from django.utils import timezone

# from apps.userApp.models import CustomUser


# # Gender Choices (for PatientProfile)
# GENDER_CHOICES = (
#     ('male', 'Male'),
#     ('female', 'Female'),
#     ('other', 'Other'),
# )



# class PatientProfile(models.Model):
#     # Relationship (FK -> Users: Patient)
#     user = models.OneToOneField(
#         CustomUser,
#         on_delete=models.CASCADE,
#         primary_key=True,
#         related_name='patient_profile',
#         limit_choices_to={'role': 'patient'} # Ensures only 'patient' users get a profile
#     )

#     image = models.URLField(blank=True, null=True)
#     dob = models.DateField(null=True, blank=True)
#     gender = models.CharField(max_length=10, choices=GENDER_CHOICES, null=True, blank=True)
#     address = models.TextField(null=True, blank=True)
#     created_at = models.DateTimeField(default=timezone.now)

#     def __str__(self):
#         return self.user.full_name

#     class Meta:
#         verbose_name = 'Patient Profile'
#         verbose_name_plural = 'Patient Profiles'

# from django.db import models
# from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
# from django.utils import timezone

# # User Role Choices
# ROLE_CHOICES = (
#     ('super_admin', 'Super Admin'),
#     ('hospital_admin', 'Hospital Admin'),
#     ('staff', 'Staff'),
#     ('doctor', 'Doctor'),
#     ('patient', 'Patient'),
# )


# # --- USER MANAGER (Required for Custom User Model) ---
# class CustomUserManager(BaseUserManager):
#     """
#     Custom user model manager where email is the unique identifier
#     for authentication instead of usernames.
#     """
#     def create_user(self, email, password=None, **extra_fields):
#         if not email:
#             raise ValueError('The Email must be set')
#         email = self.normalize_email(email)
#         user = self.model(email=email, **extra_fields)
#         user.set_password(password)
#         user.save(using=self._db)
#         return user

#     def create_superuser(self, email, password=None, **extra_fields):
#         extra_fields.setdefault('is_staff', True)
#         extra_fields.setdefault('is_superuser', True)
#         extra_fields.setdefault('is_active', True)
#         extra_fields.setdefault('role', 'super_admin') # Set superuser role

#         if extra_fields.get('is_staff') is not True:
#             raise ValueError('Superuser must have is_staff=True.')
#         if extra_fields.get('is_superuser') is not True:
#             raise ValueError('Superuser must have is_superuser=True.')

#         return self.create_user(email, password, **extra_fields)


# # --- USERS TABLE (Custom User Model) ---
# class CustomUser(AbstractBaseUser, PermissionsMixin):
#     """
#     Centralized user table handling all roles: super admin, hospital admins,
#     staff, doctors, and patients.
#     """
#     # Required Fields
#     full_name = models.CharField(max_length=255)
#     email = models.EmailField(unique=True)
#     phone = models.CharField(max_length=20, unique=True, blank=True, null=True)

#     # Role and Status
#     role = models.CharField(
#         max_length=50,
#         choices=ROLE_CHOICES,
#         default='patient', # Default role for self-registered users
#         help_text="Defines the user's role in the system."
#     )

#     # Relationship (FK -> Hospitals)
#     # NULL for super admin and patients who aren't specifically tied to one hospital
#     hospital = models.ForeignKey(
#         'hospitalApp.Hospital',
#         on_delete=models.SET_NULL,
#         null=True,
#         blank=True,
#         related_name='users',
#         help_text="Hospital this user is associated with (Null for Super Admin/Patient)."
#     )

#     # Meta Fields
#     created_at = models.DateTimeField(default=timezone.now)

#     # Required AbstractBaseUser fields
#     is_active = models.BooleanField(default=True)
#     is_staff = models.BooleanField(default=False)
#     is_superuser = models.BooleanField(default=False)
#     last_login = models.DateTimeField(null=True, blank=True)
#     date_joined = models.DateTimeField(default=timezone.now)

#     objects = CustomUserManager()

#     USERNAME_FIELD = 'email'
#     REQUIRED_FIELDS = ['full_name', 'role']

#     def __str__(self):
#         return f"{self.full_name} ({self.role})"


