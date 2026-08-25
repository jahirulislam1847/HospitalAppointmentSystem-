from django.contrib import admin
from .models import (
    DoctorProfile,
    DoctorSchedule,
    DoctorSpecialized,
    DoctorQualification,
    DoctorReview
)


@admin.register(DoctorSpecialized)
class DoctorSpecializedAdmin(admin.ModelAdmin):
    list_display = ('name', 'created_at')
    search_fields = ('name',)


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
# Inline: Doctor Review
# -----------------------------
class DoctorReviewInline(admin.TabularInline):
    model = DoctorReview
    extra = 0
    fields = ('user', 'rating', 'comment', 'show', 'created_at')
    readonly_fields = ('user', 'rating', 'comment', 'created_at')
    can_delete = True


# -----------------------------
# Main Admin: Doctor Profile
# -----------------------------
@admin.register(DoctorProfile)
class DoctorProfileAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'chamber_room', 'fee')
    search_fields = ('user__full_name', 'chamber_room')
    list_filter = ('chamber_room',)
    readonly_fields = ('created_at',)

    inlines = [
        DoctorScheduleInline,
        DoctorQualificationInline,
        DoctorReviewInline
    ]

    def get_doctor_name(self, obj):
        return obj.user.full_name
    get_doctor_name.short_description = 'Doctor Name'


# -----------------------------
# Moderation Admin: Doctor Review
# -----------------------------
@admin.register(DoctorReview)
class DoctorReviewAdmin(admin.ModelAdmin):
    list_display = ('get_doctor_name', 'get_user_name', 'rating', 'show', 'created_at')
    list_filter = ('show', 'rating', 'created_at')
    search_fields = ('doctor__user__full_name', 'user__full_name', 'comment')
    list_editable = ('show',)  # Allows admins to toggle review visibility directly from the list view
    readonly_fields = ('created_at',)

    def get_doctor_name(self, obj):
        return f"Dr. {obj.doctor.user.full_name}"
    get_doctor_name.short_description = 'Doctor'

    def get_user_name(self, obj):
        return obj.user.full_name
    get_user_name.short_description = 'Reviewed By'