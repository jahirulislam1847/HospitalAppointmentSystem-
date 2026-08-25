from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.forms import UserCreationForm, UserChangeForm

from .models import CustomUser


class CustomUserCreationForm(UserCreationForm):
    """
    A custom form for creating new users in the admin site.
    Handles password fields correctly for CustomUser model.
    """
    class Meta:
        model = CustomUser
        # Include all necessary fields from your CustomUser model
        fields = ('email', 'full_name', 'phone', 'role', 'hospital') 
        
        
class CustomUserChangeForm(UserChangeForm):
    """
    A custom form for updating existing users in the admin site.
    """
    class Meta:
        model = CustomUser
        fields = ('email', 'full_name', 'phone', 'role', 'hospital', 'is_active', 'is_staff')



# --- 1. Custom User Admin Configuration ---

class CustomUserAdmin(BaseUserAdmin):
    """
    Custom administration panel for the CustomUser model,
    integrating user-specific fields like role, phone, and hospital.
    """
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    
    # Fields to display in the list view
    list_display = ('email', 'full_name', 'role', 'is_active')
    list_filter = ('role', 'is_active')
    search_fields = ('email', 'full_name', 'phone')
    ordering = ('email',)

    # Fields that should not be editable after creation (except password)
    readonly_fields = ('created_at',)

    # Define how the user detail page is organized
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        ('Personal Info', {'fields': ('full_name', 'phone', 'role')}),
        ('Hospital Association', {'fields': ('hospital',)}),
        ('Permissions', {
            'fields': ('is_active', 'is_staff', 'groups', 'user_permissions'),
            # 'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        ('Important dates', {'fields': ('last_login', 'created_at')}),
    )

    # Add role to the fields used when creating a user via the admin
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'full_name', 'phone', 'role', 'hospital', 'password1', 'password2'),
        }),
    )


# Unregister the default User model if it was registered (good practice)
try:
    admin.site.unregister(CustomUser)
except admin.sites.NotRegistered:
    pass

# Register the CustomUser model with the custom admin class
admin.site.register(CustomUser, CustomUserAdmin)



admin.site.index_title = "All Tables"
admin.site.site_title = "Hospital Appointment Management System"
admin.site.site_header = "Hospital Appointment Management System"