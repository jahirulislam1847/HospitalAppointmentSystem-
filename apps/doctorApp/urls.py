from django.urls import path
from .views import DoctorListView, DoctorDetailView

app_name = 'doctorApp'

urlpatterns = [
    path('', DoctorListView.as_view(), name='doctor_list'),
    path('<int:pk>/', DoctorDetailView.as_view(), name='doctor_detail'),
]