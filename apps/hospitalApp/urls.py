from django.urls import path
from .views import HospitalListView, HospitalDetailView

app_name = 'hospitalApp'

urlpatterns = [
    path('', HospitalListView.as_view(), name='hospital_list'),
    path('<slug:slug>/', HospitalDetailView.as_view(), name='hospital_detail'),
]