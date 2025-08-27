from django.urls import path
from . import views

app_name = 'students'

urlpatterns = [
    path('', views.index, name='index'),
    path('apply/', views.ApplicantCreateView.as_view(), name='applicant_create'),
    path('applicants/', views.ApplicantListView.as_view(), name='applicant_list'),
    path('applicants/<int:pk>/', views.ApplicantDetailView.as_view(), name='applicant_detail'),
    path('applicants/<int:pk>/accept/', views.accept_applicant, name='accept_applicant'),
]