from django.shortcuts import render
from apps.hospitalApp.models import Hospital
from apps.doctorApp.models import DoctorProfile

def home_view(request):
    # Fetch top 8 hospitals ordered by most views
    hospitals = Hospital.objects.prefetch_related(
        'doctors__user',
        'doctors__specialized'
    ).order_by('-search_count')[:8]

    # Fetch top 8 doctors ordered by most views
    doctors = DoctorProfile.objects.select_related(
        'user'
    ).prefetch_related(
        'hospital',
        'specialized',
        'qualification',
        'schedules'
    ).order_by('-search_count')[:8]

    context = {
        'hospitals': hospitals,
        'doctors': doctors,
    }

    return render(request, "coreApp/index.html", context)