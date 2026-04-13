# appointments/urls.py
from django.urls import path
from . import views

urlpatterns = [
    # The Home Page (where users go after logging in)
    path('', views.home, name='home'),
    
    # Dashboards
    path('doctor/dashboard/', views.doctor_dashboard, name='doctor_dashboard'),
    path('patient/dashboard/', views.patient_dashboard, name='patient_dashboard'),
    
    # Actions
    path('doctor/add-slot/', views.add_slot, name='add_slot'),
    path('book/<int:slot_id>/', views.book_appointment, name='book_appointment'),
]