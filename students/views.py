from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.urls import reverse_lazy
from django.utils import timezone
from django.views.generic import CreateView, ListView, DetailView
from accounts.decorators import admin_required
from accounts.models import User
from .models import Student, Class, Applicant
from .forms import ApplicantForm

@login_required
def index(request):
    """Student module index view"""
    return render(request, 'students/index.html', {'title': 'Student Management'})

class ApplicantCreateView(CreateView):
    model = Applicant
    form_class = ApplicantForm
    template_name = 'students/applicant_form.html'
    success_url = reverse_lazy('students:applicant_list')

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Apply for Admission'
        return context

class ApplicantListView(ListView):
    model = Applicant
    template_name = 'students/applicant_list.html'
    context_object_name = 'applicants'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Applicant List'
        return context

class ApplicantDetailView(DetailView):
    model = Applicant
    template_name = 'students/applicant_detail.html'
    context_object_name = 'applicant'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Applicant Details'
        return context

@login_required
@admin_required
def accept_applicant(request, pk):
    """Accept an applicant and create a student profile."""
    applicant = get_object_or_404(Applicant, pk=pk)

    if applicant.status == 'ACCEPTED':
        messages.warning(request, f'{applicant.first_name} {applicant.last_name} has already been accepted.')
        return redirect('students:applicant_list')

    # Create a new user
    username = f'{applicant.first_name.lower()}.{applicant.last_name.lower()}{applicant.pk}'
    user, created = User.objects.get_or_create(
        email=applicant.email,
        defaults={
            'username': username,
            'first_name': applicant.first_name,
            'last_name': applicant.last_name,
            'role': User.Role.STUDENT
        }
    )
    if created:
        user.set_unusable_password()
        user.save()

    # Create a new student profile
    year = timezone.now().year
    admission_number = f'{year}{applicant.pk:04d}'
    student, created = Student.objects.get_or_create(
        user=user,
        defaults={
            'admission_number': admission_number,
            'date_of_birth': applicant.date_of_birth,
            'gender': applicant.gender,
            'current_class': applicant.class_applying_for,
            'admission_date': timezone.now().date(),
            'parent_guardian_name': f'{applicant.first_name} {applicant.last_name}', # Placeholder
            'parent_guardian_phone': applicant.phone_number,
            'parent_guardian_email': applicant.email,
        }
    )

    # Update applicant status
    applicant.status = Applicant.Status.ACCEPTED
    applicant.save()

    messages.success(request, f'Successfully accepted {applicant.first_name} {applicant.last_name} as a student.')
    return redirect('students:applicant_list')
