from django.views.generic import ListView, DetailView
from django.db.models import F
from .models import Hospital

class HospitalListView(ListView):
    model = Hospital
    template_name = 'hospitalApp/hospital_list.html'
    context_object_name = 'hospitals'

    def get_queryset(self):
        # Prefetch related doctors and their users/specializations to optimize DB queries
        return Hospital.objects.prefetch_related(
            'doctors__user',
            'doctors__specialized'
        ).all()


class HospitalDetailView(DetailView):
    model = Hospital
    template_name = 'hospitalApp/hospital_detail.html'
    context_object_name = 'hospital'
    slug_field = 'slug'
    slug_url_kwarg = 'slug'

    def get_object(self, queryset=None):
        obj = super().get_object(queryset)
        # Atomically increment search count when hospital is viewed
        Hospital.objects.filter(pk=obj.pk).update(search_count=F('search_count') + 1)
        return obj

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Fetch doctors with all qualifications and schedules attached
        context['doctors'] = self.object.doctors.select_related('user').prefetch_related(
            'specialized',
            'qualification',
            'schedules'
        ).all()
        return context