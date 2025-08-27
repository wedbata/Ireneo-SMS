from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils.translation import gettext_lazy as _
from .forms import UserProfileForm, StudentRegistrationForm, ParentRegistrationForm, TeacherRegistrationForm, StaffRegistrationForm

@login_required
def profile(request):
    """View user profile"""
    return render(request, 'accounts/profile.html')

@login_required
def edit_profile(request):
    """Edit user profile"""
    if request.method == 'POST':
        form = UserProfileForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            messages.success(request, _('Your profile has been updated successfully.'))
            return redirect('profile')
    else:
        form = UserProfileForm(instance=request.user)
    
    return render(request, 'accounts/edit_profile.html', {'form': form})

def register_student(request):
    """Register a new student"""
    if request.method == 'POST':
        form = StudentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'STUDENT'
            user.save()
            messages.success(request, _('Student account created successfully. You can now log in.'))
            return redirect('login')
    else:
        form = StudentRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'student'})

def register_parent(request):
    """Register a new parent"""
    if request.method == 'POST':
        form = ParentRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'PARENT'
            user.save()
            messages.success(request, _('Parent account created successfully. You can now log in.'))
            return redirect('login')
    else:
        form = ParentRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'parent'})

def register_teacher(request):
    """Register a new teacher"""
    if request.method == 'POST':
        form = TeacherRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'TEACHER'
            user.save()
            messages.success(request, _('Teacher account created successfully. You can now log in.'))
            return redirect('login')
    else:
        form = TeacherRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'teacher'})

def register_staff(request):
    """Register a new staff member"""
    if request.method == 'POST':
        form = StaffRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save(commit=False)
            user.role = 'STAFF'
            user.save()
            messages.success(request, _('Staff account created successfully. You can now log in.'))
            return redirect('login')
    else:
        form = StaffRegistrationForm()
    
    return render(request, 'accounts/register.html', {'form': form, 'user_type': 'staff'})