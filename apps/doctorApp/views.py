from django.views.generic import ListView, DetailView
from django.db.models import F, Q
from .models import DoctorProfile, DoctorSpecialized

class DoctorListView(ListView):
    model = DoctorProfile
    template_name = 'doctorApp/doctor_list.html'
    context_object_name = 'doctors'

    def get_queryset(self):
        queryset = DoctorProfile.objects.select_related(
            'user', 
            'hospital'
        ).prefetch_related(
            'specialized', 
            'qualification', 
            'schedules'
        ).all()

        # Optional filters via query parameters
        search_query = self.request.GET.get('q')
        specialty_id = self.request.GET.get('specialty')

        if search_query:
            queryset = queryset.filter(
                Q(user__full_name__icontains=search_query) |
                Q(hospital__name__icontains=search_query)
            )

        if specialty_id:
            queryset = queryset.filter(specialized__id=specialty_id)

        return queryset.distinct()

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['specialties'] = DoctorSpecialized.objects.all()
        context['selected_specialty'] = self.request.GET.get('specialty', '')
        context['search_query'] = self.request.GET.get('q', '')
        return context


class DoctorDetailView(DetailView):
    model = DoctorProfile
    template_name = 'doctorApp/doctor_detail.html'
    context_object_name = 'doctor'
    pk_url_kwarg = 'pk'  # Primary key corresponds to user_id

    def get_queryset(self):
        return DoctorProfile.objects.select_related(
            'user', 
            'hospital'
        ).prefetch_related(
            'specialized', 
            'qualification', 
            'schedules'
        )

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Atomically increment search view count
        DoctorProfile.objects.filter(pk=obj.pk).update(search_count=F('search_count') + 1)
        return obj