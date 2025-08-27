from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
import os
from accounts.models import User
from decimal import Decimal

class Department(models.Model):
    """Department model"""
    name = models.CharField(max_length=100, verbose_name=_('Department Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Department Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    head = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='headed_departments', 
                           verbose_name=_('Department Head'))
    is_academic = models.BooleanField(default=True, verbose_name=_('Is Academic'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Department')
        verbose_name_plural = _('Departments')
    
    def __str__(self):
        return self.name

class Designation(models.Model):
    """Staff designation model"""
    name = models.CharField(max_length=100, verbose_name=_('Designation Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Designation Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_teaching = models.BooleanField(default=False, verbose_name=_('Is Teaching Position'))
    rank_order = models.PositiveSmallIntegerField(default=0, verbose_name=_('Rank Order'))
    
    class Meta:
        verbose_name = _('Designation')
        verbose_name_plural = _('Designations')
        ordering = ['rank_order']
    
    def __str__(self):
        return self.name

def staff_document_path(instance, filename):
    """Generate file path for staff documents"""
    return f'staff/{instance.staff.employee_id}/documents/{filename}'

class StaffProfile(models.Model):
    """Staff profile model extending the User model"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='staff_profile')
    employee_id = models.CharField(max_length=50, unique=True, verbose_name=_('Employee ID'))
    department = models.ForeignKey(Department, on_delete=models.SET_NULL, null=True, related_name='staff', 
                                  verbose_name=_('Department'))
    designation = models.ForeignKey(Designation, on_delete=models.SET_NULL, null=True, related_name='staff', 
                                   verbose_name=_('Designation'))
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
    date_of_joining = models.DateField(verbose_name=_('Date of Joining'))
    contract_type = models.CharField(
        max_length=20,
        choices=[
            ('permanent', _('Permanent')),
            ('contract', _('Contract')),
            ('part_time', _('Part Time')),
            ('temporary', _('Temporary'))
        ],
        default='permanent',
        verbose_name=_('Contract Type')
    )
    contract_end_date = models.DateField(null=True, blank=True, verbose_name=_('Contract End Date'))
    qualification = models.CharField(max_length=100, verbose_name=_('Qualification'))
    experience = models.CharField(max_length=100, blank=True, verbose_name=_('Experience'))
    emergency_contact = models.CharField(max_length=20, verbose_name=_('Emergency Contact'))
    blood_group = models.CharField(max_length=5, blank=True, verbose_name=_('Blood Group'))
    address = models.TextField(blank=True, verbose_name=_('Address'))
    national_id = models.CharField(max_length=50, blank=True, verbose_name=_('National ID'))
    bank_account_name = models.CharField(max_length=100, blank=True, verbose_name=_('Bank Account Name'))
    bank_account_number = models.CharField(max_length=50, blank=True, verbose_name=_('Bank Account Number'))
    bank_name = models.CharField(max_length=100, blank=True, verbose_name=_('Bank Name'))
    bank_branch = models.CharField(max_length=100, blank=True, verbose_name=_('Bank Branch'))
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Basic Salary'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Staff Profile')
        verbose_name_plural = _('Staff Profiles')
    
    def __str__(self):
        return f"{self.employee_id} - {self.user.get_full_name()}"
    
    @property
    def is_teacher(self):
        """Check if staff is a teacher"""
        return self.designation.is_teaching if self.designation else False
    
    @property
    def years_of_service(self):
        """Calculate years of service"""
        today = timezone.now().date()
        delta = today - self.date_of_joining
        return delta.days // 365

class StaffDocument(models.Model):
    """Staff document model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='documents', 
                             verbose_name=_('Staff'))
    document_type = models.CharField(max_length=50, verbose_name=_('Document Type'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    file = models.FileField(upload_to=staff_document_path, verbose_name=_('File'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))
    
    class Meta:
        verbose_name = _('Staff Document')
        verbose_name_plural = _('Staff Documents')
    
    def __str__(self):
        return f"{self.staff} - {self.document_type}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class LeaveType(models.Model):
    """Leave type model"""
    name = models.CharField(max_length=100, verbose_name=_('Leave Type'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Leave Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    max_days_allowed = models.PositiveSmallIntegerField(default=0, verbose_name=_('Maximum Days Allowed'))
    is_paid = models.BooleanField(default=True, verbose_name=_('Is Paid Leave'))
    requires_attachment = models.BooleanField(default=False, verbose_name=_('Requires Attachment'))
    
    class Meta:
        verbose_name = _('Leave Type')
        verbose_name_plural = _('Leave Types')
    
    def __str__(self):
        return self.name

def leave_attachment_path(instance, filename):
    """Generate file path for leave attachments"""
    return f'staff/{instance.staff.employee_id}/leave_attachments/{filename}'

class LeaveApplication(models.Model):
    """Leave application model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_applications', 
                             verbose_name=_('Staff'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='applications', 
                                  verbose_name=_('Leave Type'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    reason = models.TextField(verbose_name=_('Reason'))
    attachment = models.FileField(upload_to=leave_attachment_path, blank=True, null=True, 
                                 verbose_name=_('Attachment'))
    application_date = models.DateField(auto_now_add=True, verbose_name=_('Application Date'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected')),
        ('cancelled', _('Cancelled'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_leaves', verbose_name=_('Approved By'))
    approval_date = models.DateField(null=True, blank=True, verbose_name=_('Approval Date'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Leave Application')
        verbose_name_plural = _('Leave Applications')
        ordering = ['-application_date']
    
    def __str__(self):
        return f"{self.staff} - {self.leave_type} ({self.start_date} to {self.end_date})"
    
    @property
    def days_requested(self):
        """Calculate number of days requested"""
        delta = self.end_date - self.start_date
        return delta.days + 1
    
    @property
    def is_past_due(self):
        """Check if leave start date is in the past"""
        return timezone.now().date() > self.start_date

class LeaveBalance(models.Model):
    """Leave balance model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='leave_balances', 
                             verbose_name=_('Staff'))
    leave_type = models.ForeignKey(LeaveType, on_delete=models.CASCADE, related_name='balances', 
                                  verbose_name=_('Leave Type'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    total_days = models.PositiveSmallIntegerField(default=0, verbose_name=_('Total Days'))
    days_taken = models.PositiveSmallIntegerField(default=0, verbose_name=_('Days Taken'))
    
    class Meta:
        verbose_name = _('Leave Balance')
        verbose_name_plural = _('Leave Balances')
        unique_together = ('staff', 'leave_type', 'academic_year')
    
    def __str__(self):
        return f"{self.staff} - {self.leave_type} ({self.academic_year})"
    
    @property
    def days_remaining(self):
        """Calculate days remaining"""
        return self.total_days - self.days_taken

class SalaryComponent(models.Model):
    """Salary component model"""
    name = models.CharField(max_length=100, verbose_name=_('Component Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Component Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    TYPE_CHOICES = [
        ('earning', _('Earning')),
        ('deduction', _('Deduction'))
    ]
    
    component_type = models.CharField(max_length=20, choices=TYPE_CHOICES, verbose_name=_('Component Type'))
    is_taxable = models.BooleanField(default=True, verbose_name=_('Is Taxable'))
    is_fixed = models.BooleanField(default=True, verbose_name=_('Is Fixed Amount'))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
                                    verbose_name=_('Percentage of Basic'))
    
    class Meta:
        verbose_name = _('Salary Component')
        verbose_name_plural = _('Salary Components')
    
    def __str__(self):
        return f"{self.name} ({self.get_component_type_display()})"

class StaffSalaryStructure(models.Model):
    """Staff salary structure model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='salary_structures', 
                             verbose_name=_('Staff'))
    effective_date = models.DateField(verbose_name=_('Effective Date'))
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Basic Salary'))
    
    class Meta:
        verbose_name = _('Staff Salary Structure')
        verbose_name_plural = _('Staff Salary Structures')
        ordering = ['-effective_date']
    
    def __str__(self):
        return f"{self.staff} - {self.effective_date}"

class SalaryStructureComponent(models.Model):
    """Salary structure component model"""
    salary_structure = models.ForeignKey(StaffSalaryStructure, on_delete=models.CASCADE, 
                                        related_name='components', verbose_name=_('Salary Structure'))
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, related_name='structure_components', 
                                 verbose_name=_('Component'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Amount'))
    
    class Meta:
        verbose_name = _('Salary Structure Component')
        verbose_name_plural = _('Salary Structure Components')
        unique_together = ('salary_structure', 'component')
    
    def __str__(self):
        return f"{self.salary_structure.staff} - {self.component}"
    
    def calculate_amount(self):
        """Calculate component amount based on percentage or fixed amount"""
        if not self.component.is_fixed:
            return (self.salary_structure.basic_salary * self.component.percentage) / Decimal('100.0')
        return self.amount

class PayrollPeriod(models.Model):
    """Payroll period model"""
    name = models.CharField(max_length=100, verbose_name=_('Period Name'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Payroll Period')
        verbose_name_plural = _('Payroll Periods')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.name} ({self.start_date} to {self.end_date})"

class Payslip(models.Model):
    """Payslip model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='payslips', 
                             verbose_name=_('Staff'))
    period = models.ForeignKey(PayrollPeriod, on_delete=models.CASCADE, related_name='payslips', 
                              verbose_name=_('Payroll Period'))
    basic_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Basic Salary'))
    total_earnings = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Earnings'))
    total_deductions = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Deductions'))
    net_salary = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Net Salary'))
    generation_date = models.DateField(auto_now_add=True, verbose_name=_('Generation Date'))
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('approved', _('Approved')),
        ('paid', _('Paid'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                             verbose_name=_('Status'))
    payment_date = models.DateField(null=True, blank=True, verbose_name=_('Payment Date'))
    payment_method = models.CharField(max_length=50, blank=True, verbose_name=_('Payment Method'))
    payment_reference = models.CharField(max_length=100, blank=True, verbose_name=_('Payment Reference'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Payslip')
        verbose_name_plural = _('Payslips')
        unique_together = ('staff', 'period')
        ordering = ['-period__start_date']
    
    def __str__(self):
        return f"{self.staff} - {self.period}"

class PayslipComponent(models.Model):
    """Payslip component model"""
    payslip = models.ForeignKey(Payslip, on_delete=models.CASCADE, related_name='components', 
                               verbose_name=_('Payslip'))
    component = models.ForeignKey(SalaryComponent, on_delete=models.CASCADE, related_name='payslip_components', 
                                 verbose_name=_('Component'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    
    class Meta:
        verbose_name = _('Payslip Component')
        verbose_name_plural = _('Payslip Components')
        unique_together = ('payslip', 'component')
    
    def __str__(self):
        return f"{self.payslip.staff} - {self.component}"

class TrainingProgram(models.Model):
    """Training program model"""
    name = models.CharField(max_length=200, verbose_name=_('Program Name'))
    description = models.TextField(verbose_name=_('Description'))
    provider = models.CharField(max_length=100, verbose_name=_('Provider'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    location = models.CharField(max_length=100, verbose_name=_('Location'))
    cost = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, verbose_name=_('Cost'))
    max_participants = models.PositiveSmallIntegerField(default=0, verbose_name=_('Maximum Participants'))
    is_mandatory = models.BooleanField(default=False, verbose_name=_('Is Mandatory'))
    is_internal = models.BooleanField(default=True, verbose_name=_('Is Internal'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Training Program')
        verbose_name_plural = _('Training Programs')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name
    
    @property
    def duration_days(self):
        """Calculate duration in days"""
        delta = self.end_date - self.start_date
        return delta.days + 1

class TrainingParticipant(models.Model):
    """Training participant model"""
    training = models.ForeignKey(TrainingProgram, on_delete=models.CASCADE, related_name='participants', 
                                verbose_name=_('Training Program'))
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='trainings', 
                             verbose_name=_('Staff'))
    registration_date = models.DateField(auto_now_add=True, verbose_name=_('Registration Date'))
    
    STATUS_CHOICES = [
        ('registered', _('Registered')),
        ('attended', _('Attended')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='registered', 
                             verbose_name=_('Status'))
    feedback = models.TextField(blank=True, verbose_name=_('Feedback'))
    
    class Meta:
        verbose_name = _('Training Participant')
        verbose_name_plural = _('Training Participants')
        unique_together = ('training', 'staff')
    
    def __str__(self):
        return f"{self.staff} - {self.training}"

class Certification(models.Model):
    """Staff certification model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='certifications', 
                             verbose_name=_('Staff'))
    name = models.CharField(max_length=200, verbose_name=_('Certification Name'))
    provider = models.CharField(max_length=100, verbose_name=_('Provider'))
    issue_date = models.DateField(verbose_name=_('Issue Date'))
    expiry_date = models.DateField(null=True, blank=True, verbose_name=_('Expiry Date'))
    credential_id = models.CharField(max_length=100, blank=True, verbose_name=_('Credential ID'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Certification')
        verbose_name_plural = _('Certifications')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.staff} - {self.name}"
    
    @property
    def is_expired(self):
        """Check if certification is expired"""
        if not self.expiry_date:
            return False
        return timezone.now().date() > self.expiry_date

def certification_file_path(instance, filename):
    """Generate file path for certification files"""
    return f'staff/{instance.certification.staff.employee_id}/certifications/{filename}'

class CertificationAttachment(models.Model):
    """Certification attachment model"""
    certification = models.ForeignKey(Certification, on_delete=models.CASCADE, related_name='attachments', 
                                     verbose_name=_('Certification'))
    file = models.FileField(upload_to=certification_file_path, verbose_name=_('File'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))
    
    class Meta:
        verbose_name = _('Certification Attachment')
        verbose_name_plural = _('Certification Attachments')
    
    def __str__(self):
        return f"{self.certification} - {self.description}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class StaffAttendance(models.Model):
    """Staff attendance model"""
    staff = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='attendance_records', 
                             verbose_name=_('Staff'))
    date = models.DateField(verbose_name=_('Date'))
    
    STATUS_CHOICES = [
        ('present', _('Present')),
        ('absent', _('Absent')),
        ('late', _('Late')),
        ('half_day', _('Half Day')),
        ('on_leave', _('On Leave'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='present', 
                             verbose_name=_('Status'))
    check_in_time = models.TimeField(null=True, blank=True, verbose_name=_('Check In Time'))
    check_out_time = models.TimeField(null=True, blank=True, verbose_name=_('Check Out Time'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Staff Attendance')
        verbose_name_plural = _('Staff Attendance')
        unique_together = ('staff', 'date')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.staff} - {self.date} ({self.get_status_display()})"
    
    @property
    def hours_worked(self):
        """Calculate hours worked"""
        if not self.check_in_time or not self.check_out_time:
            return 0
        
        check_in = timezone.datetime.combine(timezone.now().date(), self.check_in_time)
        check_out = timezone.datetime.combine(timezone.now().date(), self.check_out_time)
        
        if check_out < check_in:  # Handle overnight shifts
            check_out = check_out + timezone.timedelta(days=1)
        
        delta = check_out - check_in
        return delta.total_seconds() / 3600  # Convert to hours