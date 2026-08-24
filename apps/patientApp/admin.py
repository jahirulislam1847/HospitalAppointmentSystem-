from django.contrib import admin

from .models import PatientProfile


@admin.register(PatientProfile)
class PatientProfileAdmin(admin.ModelAdmin):
    # Use user__full_name to display the patient's name directly
    list_display = ('get_patient_name', 'dob', 'gender')
    search_fields = ('user__full_name', 'address')
    list_filter = ('gender',)
    
    # Helper method to display the patient's name in the list view
    def get_patient_name(self, obj):
        return obj.user.full_name
    get_patient_name.short_description = 'Patient Name'

