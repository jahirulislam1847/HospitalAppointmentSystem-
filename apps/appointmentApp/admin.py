from django.contrib import admin

from .models import Appointment

@admin.register(Appointment)
class AppointmentAdmin(admin.ModelAdmin):
    list_display = ('patient', 'doctor', 'hospital', 'appointment_date', 'appointment_time', 'status')
    search_fields = ('patient__full_name', 'doctor__user__full_name', 'hospital__name')
    list_filter = ('status', 'hospital', 'appointment_date')
    date_hierarchy = 'appointment_date'
    readonly_fields = ('created_at', 'created_by') # Patient/Staff status should be set automatically on creation
    
    def save_model(self, request, obj, form, change):
        if not obj.pk:
            # Only set created_by when creating a new object
            obj.created_by = request.user
        super().save_model(request, obj, form, change)