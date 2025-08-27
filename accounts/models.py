from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.translation import gettext_lazy as _

class User(AbstractUser):
    """Custom user model for role-based access control"""
    
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', _('Administrator')
        PRINCIPAL = 'PRINCIPAL', _('Principal')
        TEACHER = 'TEACHER', _('Teacher')
        STAFF = 'STAFF', _('Staff')
        STUDENT = 'STUDENT', _('Student')
        PARENT = 'PARENT', _('Parent')
        FINANCE = 'FINANCE', _('Finance Officer')
        LIBRARIAN = 'LIBRARIAN', _('Librarian')
    
    role = models.CharField(
        max_length=20,
        choices=Role.choices,
        default=Role.STUDENT,
        verbose_name=_('Role')
    )
    
    # Additional fields
    phone_number = models.CharField(max_length=20, blank=True, verbose_name=_('Phone Number'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True, verbose_name=_('Profile Picture'))
    language_preference = models.CharField(
        max_length=2,
        choices=[('en', _('English')), ('ar', _('Arabic'))],
        default='en',
        verbose_name=_('Language Preference')
    )
    
    def __str__(self):
        return f"{self.get_full_name()} ({self.get_role_display()})"
    
    @property
    def is_admin(self):
        return self.role == self.Role.ADMIN
    
    @property
    def is_principal(self):
        return self.role == self.Role.PRINCIPAL
    
    @property
    def is_teacher(self):
        return self.role == self.Role.TEACHER
    
    @property
    def is_staff_member(self):
        return self.role == self.Role.STAFF
    
    @property
    def is_student(self):
        return self.role == self.Role.STUDENT
    
    @property
    def is_parent(self):
        return self.role == self.Role.PARENT
    
    @property
    def is_finance(self):
        return self.role == self.Role.FINANCE
    
    @property
    def is_librarian(self):
        return self.role == self.Role.LIBRARIAN