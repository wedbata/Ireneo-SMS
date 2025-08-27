from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from accounts.decorators import admin_required, principal_required, teacher_required, student_required, parent_required

def home(request):
    """Home page view"""
    return render(request, 'core/home.html')

@login_required
def dashboard(request):
    """Main dashboard view after login"""
    user = request.user
    context = {
        'user': user,
    }
    
    # Redirect to role-specific dashboard if available
    if user.is_admin or user.is_principal:
        return render(request, 'core/dashboard_admin.html', context)
    elif user.is_teacher:
        return render(request, 'core/dashboard_teacher.html', context)
    elif user.is_student:
        return render(request, 'core/dashboard_student.html', context)
    elif user.is_parent:
        return render(request, 'core/dashboard_parent.html', context)
    elif user.is_finance:
        return render(request, 'core/dashboard_finance.html', context)
    elif user.is_librarian:
        return render(request, 'core/dashboard_librarian.html', context)
    else:
        return render(request, 'core/dashboard.html', context)

@admin_required
def admin_dashboard(request):
    """Admin dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard_admin.html', context)

@teacher_required
def teacher_dashboard(request):
    """Teacher dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard_teacher.html', context)

@student_required
def student_dashboard(request):
    """Student dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard_student.html', context)

@parent_required
def parent_dashboard(request):
    """Parent dashboard view"""
    context = {
        'user': request.user,
    }
    return render(request, 'core/dashboard_parent.html', context)