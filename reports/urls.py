from django.urls import path
from . import views

app_name = 'reports'

urlpatterns = [
    path('attendance/', views.attendance_report, name='attendance_report'),
]
