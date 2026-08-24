from django.contrib import admin
from .models import (
    DoctorProfile,
    DoctorSchedule,
    DoctorSpecialized,
    DoctorQualification
)


@admin.register(DoctorSpecialized)
class DoctorSpecializedAdmin(admin.ModelAdmin):
    pass

# -----------------------------
# Inline: Doctor Schedules
# -----------------------------
class DoctorScheduleInline(admin.StackedInline):
    model = DoctorSchedule
    extra = 1
    autocomplete_fields = ['created_by']


# -----------------------------
# Inline: Doctor Qualification
# -----------------------------
class DoctorQualificationInline(admin.StackedInline):
    model = DoctorQualification
    extra = 1


# -----------------------------
# Main Admin: Doctor Profile
# -----------------------------
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'hospital', 'chamber_room', 'fee')
    search_fields = ('user__full_name', 'chamber_room')
    list_filter = ('hospital', 'chamber_room')
    readonly_fields = ('created_at',)

    inlines = [
        DoctorScheduleInline,
        DoctorQualificationInline
    ]

    def get_doctor_name(self, obj):
        return obj.user.full_name
    get_doctor_name.short_description = 'Doctor Name'


# -----------------------------
# Optional: Register Schedule separately if needed
# If you DO NOT want this, delete this block.
# -----------------------------
# @admin.register(DoctorSchedule)
# class DoctorScheduleAdmin(admin.ModelAdmin):
#     pass

# @admin.register(DoctorQualification)
# class DoctorQualificationAdmin(admin.ModelAdmin):
#     pass
