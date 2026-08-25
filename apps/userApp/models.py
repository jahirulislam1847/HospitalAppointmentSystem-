from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.utils import timezone

# User Role Choices
ROLE_CHOICES = (
    ('super_admin', 'Super Admin'),
    ('hospital_admin', 'Hospital Admin'),
    ('staff', 'Staff'),
    ('doctor', 'Doctor'),
    ('patient', 'Patient'),
)


# --- USER MANAGER (Required for Custom User Model) ---
class CustomUserManager(BaseUserManager):
    """
    Custom user model manager where email is the unique identifier
    for authentication instead of usernames.
    """
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        extra_fields.setdefault('is_active', True)
        extra_fields.setdefault('role', 'super_admin') # Set superuser role

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


# --- USERS TABLE (Custom User Model) ---
class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Centralized user table handling all roles: super admin, hospital admins,
    staff, doctors, and patients.
    """
    # Required Fields
    full_name = models.CharField(max_length=255)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=20, unique=True, blank=True, null=True)

    # Role and Status
    role = models.CharField(
        max_length=50,
        choices=ROLE_CHOICES,
        default='patient', # Default role for self-registered users
        help_text="Defines the user's role in the system."
    )

    # Relationship (M-to-M -> Hospitals)
    # NULL for super admin and patients who aren't specifically tied to one hospital
    hospital = models.ManyToManyField(
        'hospitalApp.Hospital',
        related_name='users',
        help_text="Hospital this user is associated with (Null for Super Admin/Patient)."
    )

    # Meta Fields
    created_at = models.DateTimeField(default=timezone.now)

    # Required AbstractBaseUser fields
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)
    last_login = models.DateTimeField(null=True, blank=True)
    date_joined = models.DateTimeField(default=timezone.now)

    objects = CustomUserManager()

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name', 'role']

    def __str__(self):
        return f"{self.full_name} ({self.role})"


