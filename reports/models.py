from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User
from students.models import Student, Class
from academics.models import Exam

class CustomReport(models.Model):
    """Custom report model for generating various reports"""
    title = models.CharField(max_length=200, verbose_name=_('Report Title'))
    report_type = models.CharField(
        max_length=50,
        choices=[
            ('student', _('Student Report')),
            ('class', _('Class Report')),
            ('exam', _('Exam Report')),
            ('attendance', _('Attendance Report')),
            ('finance', _('Finance Report')),
            ('staff', _('Staff Report'))
        ],
        verbose_name=_('Report Type')
    )
    parameters = models.JSONField(verbose_name=_('Report Parameters'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_reports', verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    is_public = models.BooleanField(default=False, verbose_name=_('Is Public'))
    
    class Meta:
        verbose_name = _('Custom Report')
        verbose_name_plural = _('Custom Reports')
    
    def __str__(self):
        return f"{self.title} ({self.get_report_type_display()})"