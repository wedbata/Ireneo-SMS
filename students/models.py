from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Class(models.Model):
    """Class/Grade model"""
    name = models.CharField(max_length=50, verbose_name=_('Class Name'))
    section = models.CharField(max_length=50, blank=True, verbose_name=_('Section'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Class')
        verbose_name_plural = _('Classes')
        unique_together = ('name', 'section', 'academic_year')
    
    def __str__(self):
        return f"{self.name} {self.section} ({self.academic_year})"

class Student(models.Model):
    """Student model extending the User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='student_profile')
    admission_number = models.CharField(max_length=50, unique=True, verbose_name=_('Admission Number'))
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'))
    gender = models.CharField(
        max_length=10,
        choices=[
            ('male', _('Male')),
            ('female', _('Female')),
            ('other', _('Other'))
        ],
        verbose_name=_('Gender')
    )
    current_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, related_name='students', verbose_name=_('Current Class'))
    admission_date = models.DateField(verbose_name=_('Admission Date'))
    parent_guardian_name = models.CharField(max_length=100, verbose_name=_('Parent/Guardian Name'))
    parent_guardian_phone = models.CharField(max_length=20, verbose_name=_('Parent/Guardian Phone'))
    parent_guardian_email = models.EmailField(blank=True, verbose_name=_('Parent/Guardian Email'))
    emergency_contact = models.CharField(max_length=20, verbose_name=_('Emergency Contact'))
    blood_group = models.CharField(max_length=5, blank=True, verbose_name=_('Blood Group'))
    medical_conditions = models.TextField(blank=True, verbose_name=_('Medical Conditions'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Student')
        verbose_name_plural = _('Students')
    
    def __str__(self):
        return f"{self.admission_number} - {self.user.get_full_name()}"

class Attendance(models.Model):
    """Student attendance model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='attendances', verbose_name=_('Student'))
    date = models.DateField(verbose_name=_('Date'))
    status = models.CharField(
        max_length=10,
        choices=[
            ('present', _('Present')),
            ('absent', _('Absent')),
            ('late', _('Late')),
            ('excused', _('Excused'))
        ],
        default='present',
        verbose_name=_('Status')
    )
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Attendance')
        verbose_name_plural = _('Attendances')
        unique_together = ('student', 'date')
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_status_display()}"

class Discipline(models.Model):
    """Discipline/Behavior log model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='discipline_records', verbose_name=_('Student'))
    date = models.DateField(verbose_name=_('Date'))
    record_type = models.CharField(
        max_length=10,
        choices=[
            ('merit', _('Merit')),
            ('demerit', _('Demerit'))
        ],
        verbose_name=_('Record Type')
    )
    description = models.TextField(verbose_name=_('Description'))
    reported_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='reported_discipline_records', verbose_name=_('Reported By'))
    
    class Meta:
        verbose_name = _('Discipline Record')
        verbose_name_plural = _('Discipline Records')
    
    def __str__(self):
        return f"{self.student} - {self.date} - {self.get_record_type_display()}"

def applicant_document_path(instance, filename):
    return f'applicants/{instance.id}/documents/{filename}'

class Applicant(models.Model):
    """Model for student applicants"""
    first_name = models.CharField(max_length=50, verbose_name=_('First Name'))
    last_name = models.CharField(max_length=50, verbose_name=_('Last Name'))
    gender = models.CharField(max_length=10, choices=[('male', _('Male')), ('female', _('Female')), ('other', _('Other'))], verbose_name=_('Gender'))
    date_of_birth = models.DateField(verbose_name=_('Date of Birth'))
    email = models.EmailField(unique=True, verbose_name=_('Email'))
    phone_number = models.CharField(max_length=20, verbose_name=_('Phone Number'))
    address = models.TextField(verbose_name=_('Address'))
    previous_school = models.CharField(max_length=100, blank=True, verbose_name=_('Previous School'))
    class_applying_for = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, verbose_name=_('Class Applying For'))
    application_date = models.DateField(auto_now_add=True, verbose_name=_('Application Date'))

    class Status(models.TextChoices):
        PENDING = 'PENDING', _('Pending')
        REVIEW = 'REVIEW', _('In Review')
        ACCEPTED = 'ACCEPTED', _('Accepted')
        REJECTED = 'REJECTED', _('Rejected')

    status = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING, verbose_name=_('Status'))

    birth_certificate = models.FileField(upload_to=applicant_document_path, blank=True, null=True, verbose_name=_('Birth Certificate'))
    previous_report_card = models.FileField(upload_to=applicant_document_path, blank=True, null=True, verbose_name=_('Previous Report Card'))

    class Meta:
        verbose_name = _('Applicant')
        verbose_name_plural = _('Applicants')
        ordering = ['-application_date']

    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.status})"


def student_document_path(instance, filename):
    return f'students/{instance.student.admission_number}/documents/{filename}'

class StudentDocument(models.Model):
    """Model for storing student documents"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='documents', verbose_name=_('Student'))
    document_type = models.CharField(max_length=50, verbose_name=_('Document Type'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    file = models.FileField(upload_to=student_document_path, verbose_name=_('File'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))

    class Meta:
        verbose_name = _('Student Document')
        verbose_name_plural = _('Student Documents')

    def __str__(self):
        return f"{self.student} - {self.document_type}"