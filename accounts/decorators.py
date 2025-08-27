from django.contrib.auth import REDIRECT_FIELD_NAME
from django.contrib.auth.decorators import user_passes_test
from django.shortcuts import redirect
from functools import wraps

def role_required(role):
    """Decorator for views that checks that the user has the specified role."""
    def check_role(user):
        return user.is_authenticated and getattr(user, f'is_{role.lower()}', False)
    
    return user_passes_test(check_role)

def admin_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is an admin."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_admin,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def principal_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a principal."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_principal,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def teacher_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a teacher."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_teacher,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def staff_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a staff member."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_staff_member,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def student_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a student."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_student,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def parent_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a parent."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_parent,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def finance_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a finance officer."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_finance,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator

def librarian_required(function=None, redirect_field_name=REDIRECT_FIELD_NAME):
    """Decorator for views that checks that the user is a librarian."""
    actual_decorator = user_passes_test(
        lambda u: u.is_authenticated and u.is_librarian,
        login_url='login',
        redirect_field_name=redirect_field_name
    )
    if function:
        return actual_decorator(function)
    return actual_decorator