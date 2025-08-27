from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os
from decimal import Decimal
from accounts.models import User
from students.models import Student, Class

class FeeCategory(models.Model):
    """Fee category model"""
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Category Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    is_optional = models.BooleanField(default=False, verbose_name=_('Optional Fee'))
    is_one_time = models.BooleanField(default=False, verbose_name=_('One Time Fee'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Fee Category')
        verbose_name_plural = _('Fee Categories')
    
    def __str__(self):
        return self.name

class FeeStructure(models.Model):
    """Fee structure model"""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='fee_structures', 
                                 verbose_name=_('Class'))
    category = models.ForeignKey(FeeCategory, on_delete=models.CASCADE, related_name='fee_structures', 
                                verbose_name=_('Category'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    term = models.CharField(max_length=20, verbose_name=_('Term'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    late_fee = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                  verbose_name=_('Late Fee'))
    late_fee_type = models.CharField(
        max_length=20,
        choices=[
            ('fixed', _('Fixed Amount')),
            ('percentage', _('Percentage'))
        ],
        default='fixed',
        verbose_name=_('Late Fee Type')
    )
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Fee Structure')
        verbose_name_plural = _('Fee Structures')
        unique_together = ('class_obj', 'category', 'academic_year', 'term')
    
    def __str__(self):
        return f"{self.class_obj} - {self.category} - {self.academic_year} - {self.term}"
    
    def calculate_late_fee(self, payment_date):
        """Calculate late fee if payment is past due date"""
        if payment_date <= self.due_date:
            return Decimal('0.00')
        
        if self.late_fee_type == 'fixed':
            return self.late_fee
        else:  # percentage
            return (self.amount * self.late_fee) / Decimal('100.0')

class StudentFee(models.Model):
    """Student fee model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fees', 
                               verbose_name=_('Student'))
    fee_structure = models.ForeignKey(FeeStructure, on_delete=models.CASCADE, related_name='student_fees', 
                                     verbose_name=_('Fee Structure'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    discount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                  verbose_name=_('Discount'))
    net_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Net Amount'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                     verbose_name=_('Amount Paid'))
    balance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Balance'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('partial', _('Partially Paid')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue')),
        ('waived', _('Waived'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    
    class Meta:
        verbose_name = _('Student Fee')
        verbose_name_plural = _('Student Fees')
        unique_together = ('student', 'fee_structure')
    
    def __str__(self):
        return f"{self.student} - {self.fee_structure}"
    
    def save(self, *args, **kwargs):
        """Override save to calculate net amount and balance"""
        self.net_amount = self.amount - self.discount
        self.balance = self.net_amount - self.amount_paid
        
        # Update status based on payment
        if self.balance <= 0:
            self.status = 'paid'
        elif self.amount_paid > 0:
            self.status = 'partial'
        elif timezone.now().date() > self.due_date and self.balance > 0:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)

class Payment(models.Model):
    """Payment model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payments', 
                               verbose_name=_('Student'))
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payments', 
                                   verbose_name=_('Student Fee'))
    amount_paid = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount Paid'))
    payment_date = models.DateField(verbose_name=_('Payment Date'))
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('Cash')),
            ('bank_transfer', _('Bank Transfer')),
            ('mobile_money', _('Mobile Money')),
            ('check', _('Check')),
            ('mtn_mobile_money', _('MTN Mobile Money')),
            ('kcb_bank', _('KCB Bank')),
            ('equity_bank', _('Equity Bank'))
        ],
        verbose_name=_('Payment Method')
    )
    transaction_id = models.CharField(max_length=100, blank=True, verbose_name=_('Transaction ID'))
    received_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='received_payments', verbose_name=_('Received By'))
    receipt_number = models.CharField(max_length=50, unique=True, verbose_name=_('Receipt Number'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Payment')
        verbose_name_plural = _('Payments')
        ordering = ['-payment_date']
    
    def __str__(self):
        return f"{self.student} - {self.amount_paid} - {self.payment_date}"
    
    def save(self, *args, **kwargs):
        """Override save to update student fee"""
        super().save(*args, **kwargs)
        
        # Update student fee
        student_fee = self.student_fee
        total_paid = student_fee.payments.aggregate(models.Sum('amount_paid'))['amount_paid__sum'] or Decimal('0.00')
        student_fee.amount_paid = total_paid
        student_fee.save()

class PaymentPlan(models.Model):
    """Payment plan model for installments"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_plans', 
                               verbose_name=_('Student'))
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='payment_plans', 
                                   verbose_name=_('Student Fee'))
    total_amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Total Amount'))
    number_of_installments = models.PositiveSmallIntegerField(verbose_name=_('Number of Installments'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_payment_plans', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    STATUS_CHOICES = [
        ('active', _('Active')),
        ('completed', _('Completed')),
        ('defaulted', _('Defaulted')),
        ('cancelled', _('Cancelled'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='active', 
                             verbose_name=_('Status'))
    
    class Meta:
        verbose_name = _('Payment Plan')
        verbose_name_plural = _('Payment Plans')
    
    def __str__(self):
        return f"{self.student} - {self.student_fee} - {self.number_of_installments} installments"

class PaymentInstallment(models.Model):
    """Payment installment model"""
    payment_plan = models.ForeignKey(PaymentPlan, on_delete=models.CASCADE, related_name='installments', 
                                    verbose_name=_('Payment Plan'))
    installment_number = models.PositiveSmallIntegerField(verbose_name=_('Installment Number'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('paid', _('Paid')),
        ('overdue', _('Overdue'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    payment = models.ForeignKey(Payment, on_delete=models.SET_NULL, null=True, blank=True, 
                               related_name='installment', verbose_name=_('Payment'))
    
    class Meta:
        verbose_name = _('Payment Installment')
        verbose_name_plural = _('Payment Installments')
        unique_together = ('payment_plan', 'installment_number')
        ordering = ['installment_number']
    
    def __str__(self):
        return f"{self.payment_plan.student} - Installment {self.installment_number}"

class ScholarshipType(models.Model):
    """Scholarship type model"""
    name = models.CharField(max_length=100, verbose_name=_('Scholarship Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                               verbose_name=_('Fixed Amount'))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
                                    verbose_name=_('Percentage'))
    is_full = models.BooleanField(default=False, verbose_name=_('Full Scholarship'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Scholarship Type')
        verbose_name_plural = _('Scholarship Types')
    
    def __str__(self):
        return self.name

class Scholarship(models.Model):
    """Scholarship model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='scholarships', 
                               verbose_name=_('Student'))
    scholarship_type = models.ForeignKey(ScholarshipType, on_delete=models.CASCADE, 
                                        related_name='scholarships', verbose_name=_('Scholarship Type'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                               verbose_name=_('Amount'))
    percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00, 
                                    verbose_name=_('Percentage'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='approved_scholarships', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Approved At'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    
    class Meta:
        verbose_name = _('Scholarship')
        verbose_name_plural = _('Scholarships')
    
    def __str__(self):
        return f"{self.student} - {self.scholarship_type} ({self.academic_year})"

class FeeWaiver(models.Model):
    """Fee waiver model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='fee_waivers', 
                               verbose_name=_('Student'))
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, related_name='waivers', 
                                   verbose_name=_('Student Fee'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    reason = models.TextField(verbose_name=_('Reason'))
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='approved_waivers', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Approved At'))
    
    class Meta:
        verbose_name = _('Fee Waiver')
        verbose_name_plural = _('Fee Waivers')
    
    def __str__(self):
        return f"{self.student} - {self.student_fee} - {self.amount}"
    
    def save(self, *args, **kwargs):
        """Override save to update student fee"""
        super().save(*args, **kwargs)
        
        # Update student fee
        student_fee = self.student_fee
        student_fee.discount += self.amount
        student_fee.save()

class ExpenseCategory(models.Model):
    """Expense category model"""
    name = models.CharField(max_length=100, unique=True, verbose_name=_('Category Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Category Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    budget_allocation = models.DecimalField(max_digits=12, decimal_places=2, default=0.00, 
                                          verbose_name=_('Budget Allocation'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))

    class Meta:
        verbose_name = _('Expense Category')
        verbose_name_plural = _('Expense Categories')

    def __str__(self):
        return self.name

def expense_receipt_path(instance, filename):
    """Generate file path for expense receipts"""
    return f'expense_receipts/{instance.id}/{filename}'

class Expense(models.Model):
    """Expense model"""
    category = models.ForeignKey(ExpenseCategory, on_delete=models.PROTECT, related_name='expenses', 
                                verbose_name=_('Category'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    date = models.DateField(verbose_name=_('Date of Expense'))
    description = models.TextField(verbose_name=_('Description'))
    paid_to = models.CharField(max_length=100, blank=True, verbose_name=_('Paid To'))
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('cash', _('Cash')),
            ('bank_transfer', _('Bank Transfer')),
            ('mobile_money', _('Mobile Money')),
            ('check', _('Check'))
        ],
        default='cash',
        verbose_name=_('Payment Method')
    )
    reference_number = models.CharField(max_length=100, blank=True, verbose_name=_('Reference Number'))
    receipt = models.FileField(upload_to=expense_receipt_path, blank=True, null=True, 
                              verbose_name=_('Receipt'))
    recorded_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='recorded_expenses', verbose_name=_('Recorded By'))
    recorded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Recorded At'))
    approved_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='approved_expenses', verbose_name=_('Approved By'))
    approved_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Approved At'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending Approval')),
        ('approved', _('Approved')),
        ('rejected', _('Rejected'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))

    class Meta:
        verbose_name = _('Expense')
        verbose_name_plural = _('Expenses')
        ordering = ['-date']

    def __str__(self):
        return f"{self.category} - {self.amount} on {self.date}"

class Budget(models.Model):
    """Budget model"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2, verbose_name=_('Total Amount'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    created_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                  related_name='created_budgets', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('active', _('Active')),
        ('closed', _('Closed'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                             verbose_name=_('Status'))
    
    class Meta:
        verbose_name = _('Budget')
        verbose_name_plural = _('Budgets')
        ordering = ['-start_date']
    
    def __str__(self):
        return f"{self.title} ({self.academic_year})"

class BudgetAllocation(models.Model):
    """Budget allocation model"""
    budget = models.ForeignKey(Budget, on_delete=models.CASCADE, related_name='allocations', 
                              verbose_name=_('Budget'))
    expense_category = models.ForeignKey(ExpenseCategory, on_delete=models.CASCADE, 
                                        related_name='budget_allocations', verbose_name=_('Expense Category'))
    allocated_amount = models.DecimalField(max_digits=12, decimal_places=2, 
                                          verbose_name=_('Allocated Amount'))
    
    class Meta:
        verbose_name = _('Budget Allocation')
        verbose_name_plural = _('Budget Allocations')
        unique_together = ('budget', 'expense_category')
    
    def __str__(self):
        return f"{self.budget} - {self.expense_category} - {self.allocated_amount}"

class FinancialYear(models.Model):
    """Financial year model"""
    name = models.CharField(max_length=50, verbose_name=_('Name'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    is_active = models.BooleanField(default=False, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Financial Year')
        verbose_name_plural = _('Financial Years')
        ordering = ['-start_date']
    
    def __str__(self):
        return self.name

class PaymentGateway(models.Model):
    """Payment gateway model"""
    name = models.CharField(max_length=100, verbose_name=_('Gateway Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Gateway Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    GATEWAY_CHOICES = [
        ('mtn_mobile_money', _('MTN Mobile Money')),
        ('kcb_bank', _('KCB Bank')),
        ('equity_bank', _('Equity Bank')),
        ('manual', _('Manual Processing'))
    ]
    
    gateway_type = models.CharField(max_length=50, choices=GATEWAY_CHOICES, 
                                   verbose_name=_('Gateway Type'))
    api_key = models.CharField(max_length=255, blank=True, verbose_name=_('API Key'))
    api_secret = models.CharField(max_length=255, blank=True, verbose_name=_('API Secret'))
    merchant_id = models.CharField(max_length=100, blank=True, verbose_name=_('Merchant ID'))
    callback_url = models.URLField(blank=True, verbose_name=_('Callback URL'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Payment Gateway')
        verbose_name_plural = _('Payment Gateways')
    
    def __str__(self):
        return self.name

class PaymentTransaction(models.Model):
    """Payment transaction model for online payments"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='payment_transactions', 
                               verbose_name=_('Student'))
    student_fee = models.ForeignKey(StudentFee, on_delete=models.CASCADE, 
                                   related_name='payment_transactions', verbose_name=_('Student Fee'))
    gateway = models.ForeignKey(PaymentGateway, on_delete=models.PROTECT, related_name='transactions', 
                               verbose_name=_('Payment Gateway'))
    amount = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Amount'))
    transaction_id = models.CharField(max_length=100, unique=True, verbose_name=_('Transaction ID'))
    reference_number = models.CharField(max_length=100, blank=True, verbose_name=_('Reference Number'))
    initiated_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Initiated At'))
    completed_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Completed At'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed')),
        ('cancelled', _('Cancelled'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    response_data = models.JSONField(null=True, blank=True, verbose_name=_('Response Data'))
    payment = models.OneToOneField(Payment, on_delete=models.SET_NULL, null=True, blank=True, 
                                  related_name='transaction', verbose_name=_('Payment'))
    
    class Meta:
        verbose_name = _('Payment Transaction')
        verbose_name_plural = _('Payment Transactions')
        ordering = ['-initiated_at']
    
    def __str__(self):
        return f"{self.student} - {self.amount} - {self.transaction_id}"