from django.db import models
from django.utils.translation import gettext_lazy as _
from accounts.models import User

class Asset(models.Model):
    """Asset model for school inventory"""
    name = models.CharField(max_length=100, verbose_name=_('Asset Name'))
    asset_id = models.CharField(max_length=50, unique=True, verbose_name=_('Asset ID'))
    category = models.CharField(
        max_length=50,
        choices=[
            ('furniture', _('Furniture')),
            ('electronics', _('Electronics')),
            ('lab_equipment', _('Laboratory Equipment')),
            ('sports', _('Sports Equipment')),
            ('books', _('Books')),
            ('other', _('Other'))
        ],
        verbose_name=_('Category')
    )
    purchase_date = models.DateField(verbose_name=_('Purchase Date'))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Purchase Price'))
    condition = models.CharField(
        max_length=20,
        choices=[
            ('new', _('New')),
            ('good', _('Good')),
            ('fair', _('Fair')),
            ('poor', _('Poor')),
            ('damaged', _('Damaged'))
        ],
        default='new',
        verbose_name=_('Condition')
    )
    location = models.CharField(max_length=100, verbose_name=_('Location'))
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='assigned_assets', verbose_name=_('Assigned To'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
    
    def __str__(self):
        return f"{self.asset_id} - {self.name}"

class Maintenance(models.Model):
    """Maintenance record model"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records', verbose_name=_('Asset'))
    maintenance_date = models.DateField(verbose_name=_('Maintenance Date'))
    description = models.TextField(verbose_name=_('Description'))
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Cost'))
    performed_by = models.CharField(max_length=100, verbose_name=_('Performed By'))
    next_maintenance_date = models.DateField(null=True, blank=True, verbose_name=_('Next Maintenance Date'))
    
    class Meta:
        verbose_name = _('Maintenance Record')
        verbose_name_plural = _('Maintenance Records')
    
    def __str__(self):
        return f"{self.asset} - {self.maintenance_date}"