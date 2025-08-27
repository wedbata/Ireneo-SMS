from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os
from accounts.models import User
from students.models import Student, Class

class AssetCategory(models.Model):
    """Asset category model"""
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Category Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Asset Category')
        verbose_name_plural = _('Asset Categories')
    
    def __str__(self):
        return self.name

class Asset(models.Model):
    """Asset model for school inventory"""
    name = models.CharField(max_length=100, verbose_name=_('Asset Name'))
    asset_id = models.CharField(max_length=50, unique=True, verbose_name=_('Asset ID'))
    category = models.ForeignKey(AssetCategory, on_delete=models.CASCADE, related_name='assets',
                                verbose_name=_('Category'))
    purchase_date = models.DateField(verbose_name=_('Purchase Date'))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Purchase Price'))
    supplier = models.CharField(max_length=100, blank=True, verbose_name=_('Supplier'))
    warranty_expiry = models.DateField(null=True, blank=True, verbose_name=_('Warranty Expiry'))
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
    assigned_to = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, 
                                   related_name='assigned_assets', verbose_name=_('Assigned To'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Asset')
        verbose_name_plural = _('Assets')
    
    def __str__(self):
        return f"{self.asset_id} - {self.name}"

class Maintenance(models.Model):
    """Maintenance record model"""
    asset = models.ForeignKey(Asset, on_delete=models.CASCADE, related_name='maintenance_records', 
                             verbose_name=_('Asset'))
    maintenance_date = models.DateField(verbose_name=_('Maintenance Date'))
    description = models.TextField(verbose_name=_('Description'))
    cost = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Cost'))
    performed_by = models.CharField(max_length=100, verbose_name=_('Performed By'))
    next_maintenance_date = models.DateField(null=True, blank=True, 
                                            verbose_name=_('Next Maintenance Date'))
    
    class Meta:
        verbose_name = _('Maintenance Record')
        verbose_name_plural = _('Maintenance Records')
    
    def __str__(self):
        return f"{self.asset} - {self.maintenance_date}"

# Library Management Models
class BookCategory(models.Model):
    """Book category model"""
    name = models.CharField(max_length=100, verbose_name=_('Category Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Category Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Book Category')
        verbose_name_plural = _('Book Categories')
    
    def __str__(self):
        return self.name

class Book(models.Model):
    """Book model for library"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    isbn = models.CharField(max_length=20, unique=True, verbose_name=_('ISBN'))
    author = models.CharField(max_length=100, verbose_name=_('Author'))
    publisher = models.CharField(max_length=100, blank=True, verbose_name=_('Publisher'))
    publication_year = models.PositiveSmallIntegerField(null=True, blank=True, 
                                                      verbose_name=_('Publication Year'))
    category = models.ForeignKey(BookCategory, on_delete=models.CASCADE, related_name='books', 
                                verbose_name=_('Category'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    pages = models.PositiveSmallIntegerField(null=True, blank=True, verbose_name=_('Pages'))
    quantity = models.PositiveSmallIntegerField(default=1, verbose_name=_('Quantity'))
    available = models.PositiveSmallIntegerField(default=1, verbose_name=_('Available'))
    location = models.CharField(max_length=100, blank=True, verbose_name=_('Shelf Location'))
    acquisition_date = models.DateField(default=timezone.now, verbose_name=_('Acquisition Date'))
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True, 
                              verbose_name=_('Price'))
    
    class Meta:
        verbose_name = _('Book')
        verbose_name_plural = _('Books')
    
    def __str__(self):
        return f"{self.title} by {self.author}"

class BookIssue(models.Model):
    """Book issue model for library"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='issues', 
                            verbose_name=_('Book'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='book_issues', 
                               verbose_name=_('Student'))
    issue_date = models.DateField(default=timezone.now, verbose_name=_('Issue Date'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    return_date = models.DateField(null=True, blank=True, verbose_name=_('Return Date'))
    
    STATUS_CHOICES = [
        ('issued', _('Issued')),
        ('returned', _('Returned')),
        ('overdue', _('Overdue')),
        ('lost', _('Lost'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='issued', 
                             verbose_name=_('Status'))
    fine_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00, 
                                     verbose_name=_('Fine Amount'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    issued_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                 related_name='issued_books', verbose_name=_('Issued By'))
    
    class Meta:
        verbose_name = _('Book Issue')
        verbose_name_plural = _('Book Issues')
        ordering = ['-issue_date']
    
    def __str__(self):
        return f"{self.book} - {self.student} - {self.issue_date}"
    
    def save(self, *args, **kwargs):
        """Override save to update book availability and check status"""
        is_new = self.pk is None
        
        if is_new:
            # Decrease available count when issuing a book
            self.book.available -= 1
            self.book.save()
        
        # Check if book is overdue
        if not self.return_date and timezone.now().date() > self.due_date:
            self.status = 'overdue'
        
        super().save(*args, **kwargs)

# Transport Management Models
class Vehicle(models.Model):
    """Vehicle model for transport management"""
    name = models.CharField(max_length=100, verbose_name=_('Vehicle Name'))
    registration_number = models.CharField(max_length=50, unique=True, 
                                          verbose_name=_('Registration Number'))
    vehicle_type = models.CharField(
        max_length=20,
        choices=[
            ('bus', _('Bus')),
            ('van', _('Van')),
            ('car', _('Car')),
            ('truck', _('Truck')),
            ('other', _('Other'))
        ],
        verbose_name=_('Vehicle Type')
    )
    capacity = models.PositiveSmallIntegerField(verbose_name=_('Seating Capacity'))
    make = models.CharField(max_length=50, verbose_name=_('Make'))
    model = models.CharField(max_length=50, verbose_name=_('Model'))
    year = models.PositiveSmallIntegerField(verbose_name=_('Year'))
    purchase_date = models.DateField(verbose_name=_('Purchase Date'))
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2, 
                                        verbose_name=_('Purchase Price'))
    insurance_expiry = models.DateField(verbose_name=_('Insurance Expiry'))
    license_expiry = models.DateField(verbose_name=_('License Expiry'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Vehicle')
        verbose_name_plural = _('Vehicles')
    
    def __str__(self):
        return f"{self.name} ({self.registration_number})"

class Driver(models.Model):
    """Driver model for transport management"""
    name = models.CharField(max_length=100, verbose_name=_('Driver Name'))
    employee_id = models.CharField(max_length=50, unique=True, verbose_name=_('Employee ID'))
    license_number = models.CharField(max_length=50, unique=True, verbose_name=_('License Number'))
    license_expiry = models.DateField(verbose_name=_('License Expiry'))
    contact_number = models.CharField(max_length=20, verbose_name=_('Contact Number'))
    address = models.TextField(verbose_name=_('Address'))
    date_of_joining = models.DateField(verbose_name=_('Date of Joining'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Driver')
        verbose_name_plural = _('Drivers')
    
    def __str__(self):
        return f"{self.name} ({self.employee_id})"

class Route(models.Model):
    """Route model for transport management"""
    name = models.CharField(max_length=100, verbose_name=_('Route Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Route Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    start_point = models.CharField(max_length=100, verbose_name=_('Start Point'))
    end_point = models.CharField(max_length=100, verbose_name=_('End Point'))
    distance = models.DecimalField(max_digits=10, decimal_places=2, verbose_name=_('Distance (km)'))
    estimated_time = models.PositiveSmallIntegerField(verbose_name=_('Estimated Time (minutes)'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Route')
        verbose_name_plural = _('Routes')
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class RouteStop(models.Model):
    """Route stop model for transport management"""
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='stops', 
                             verbose_name=_('Route'))
    name = models.CharField(max_length=100, verbose_name=_('Stop Name'))
    order = models.PositiveSmallIntegerField(verbose_name=_('Order'))
    arrival_time = models.TimeField(verbose_name=_('Arrival Time'))
    departure_time = models.TimeField(verbose_name=_('Departure Time'))
    
    class Meta:
        verbose_name = _('Route Stop')
        verbose_name_plural = _('Route Stops')
        unique_together = ('route', 'order')
        ordering = ['route', 'order']
    
    def __str__(self):
        return f"{self.route} - {self.name} (Stop {self.order})"

class VehicleAssignment(models.Model):
    """Vehicle assignment model for transport management"""
    vehicle = models.ForeignKey(Vehicle, on_delete=models.CASCADE, related_name='assignments', 
                               verbose_name=_('Vehicle'))
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='vehicle_assignments', 
                             verbose_name=_('Route'))
    driver = models.ForeignKey(Driver, on_delete=models.CASCADE, related_name='assignments', 
                              verbose_name=_('Driver'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(null=True, blank=True, verbose_name=_('End Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Vehicle Assignment')
        verbose_name_plural = _('Vehicle Assignments')
    
    def __str__(self):
        return f"{self.vehicle} - {self.route} - {self.driver}"

class TransportRegistration(models.Model):
    """Transport registration model for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='transport_registrations', 
                               verbose_name=_('Student'))
    route = models.ForeignKey(Route, on_delete=models.CASCADE, related_name='student_registrations', 
                             verbose_name=_('Route'))
    pickup_stop = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='pickup_registrations', 
                                   verbose_name=_('Pickup Stop'))
    dropoff_stop = models.ForeignKey(RouteStop, on_delete=models.CASCADE, related_name='dropoff_registrations', 
                                    verbose_name=_('Dropoff Stop'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    registration_date = models.DateField(auto_now_add=True, verbose_name=_('Registration Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Transport Registration')
        verbose_name_plural = _('Transport Registrations')
        unique_together = ('student', 'academic_year')
    
    def __str__(self):
        return f"{self.student} - {self.route} ({self.academic_year})"

# Hostel Management Models
class Hostel(models.Model):
    """Hostel model"""
    name = models.CharField(max_length=100, verbose_name=_('Hostel Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Hostel Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    warden = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='managed_hostels', 
                              verbose_name=_('Warden'))
    capacity = models.PositiveSmallIntegerField(verbose_name=_('Total Capacity'))
    address = models.TextField(verbose_name=_('Address'))
    contact_number = models.CharField(max_length=20, blank=True, verbose_name=_('Contact Number'))
    
    GENDER_CHOICES = [
        ('male', _('Male')),
        ('female', _('Female')),
        ('mixed', _('Mixed'))
    ]
    
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, verbose_name=_('Gender'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Hostel')
        verbose_name_plural = _('Hostels')
    
    def __str__(self):
        return f"{self.name} ({self.code})"

class Room(models.Model):
    """Room model for hostel"""
    hostel = models.ForeignKey(Hostel, on_delete=models.CASCADE, related_name='rooms', 
                              verbose_name=_('Hostel'))
    room_number = models.CharField(max_length=20, verbose_name=_('Room Number'))
    floor = models.CharField(max_length=20, verbose_name=_('Floor'))
    capacity = models.PositiveSmallIntegerField(verbose_name=_('Capacity'))
    occupied = models.PositiveSmallIntegerField(default=0, verbose_name=_('Occupied'))
    
    ROOM_TYPE_CHOICES = [
        ('standard', _('Standard')),
        ('deluxe', _('Deluxe')),
        ('dormitory', _('Dormitory'))
    ]
    
    room_type = models.CharField(max_length=20, choices=ROOM_TYPE_CHOICES, default='standard', 
                                verbose_name=_('Room Type'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Room')
        verbose_name_plural = _('Rooms')
        unique_together = ('hostel', 'room_number')
    
    def __str__(self):
        return f"{self.hostel} - Room {self.room_number} (Floor {self.floor})"

class Bed(models.Model):
    """Bed model for hostel room"""
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='beds', 
                            verbose_name=_('Room'))
    bed_number = models.CharField(max_length=20, verbose_name=_('Bed Number'))
    is_occupied = models.BooleanField(default=False, verbose_name=_('Occupied'))
    
    class Meta:
        verbose_name = _('Bed')
        verbose_name_plural = _('Beds')
        unique_together = ('room', 'bed_number')
    
    def __str__(self):
        return f"{self.room} - Bed {self.bed_number}"

class HostelAllocation(models.Model):
    """Hostel allocation model for students"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='hostel_allocations', 
                               verbose_name=_('Student'))
    bed = models.ForeignKey(Bed, on_delete=models.CASCADE, related_name='allocations', 
                           verbose_name=_('Bed'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    allocation_date = models.DateField(auto_now_add=True, verbose_name=_('Allocation Date'))
    vacated_date = models.DateField(null=True, blank=True, verbose_name=_('Vacated Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Hostel Allocation')
        verbose_name_plural = _('Hostel Allocations')
    
    def __str__(self):
        return f"{self.student} - {self.bed} ({self.academic_year})"
    
    def save(self, *args, **kwargs):
        """Override save to update bed and room occupancy"""
        is_new = self.pk is None
        
        if is_new:
            # Mark bed as occupied
            self.bed.is_occupied = True
            self.bed.save()
            
            # Increase room occupancy
            room = self.bed.room
            room.occupied += 1
            room.save()
        
        super().save(*args, **kwargs)

# Health Clinic Models
class MedicalCondition(models.Model):
    """Medical condition model"""
    name = models.CharField(max_length=100, verbose_name=_('Condition Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Medical Condition')
        verbose_name_plural = _('Medical Conditions')
    
    def __str__(self):
        return self.name

class Medicine(models.Model):
    """Medicine model for health clinic"""
    name = models.CharField(max_length=100, verbose_name=_('Medicine Name'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    quantity = models.PositiveIntegerField(default=0, verbose_name=_('Quantity'))
    unit = models.CharField(max_length=20, verbose_name=_('Unit'))
    expiry_date = models.DateField(verbose_name=_('Expiry Date'))
    
    class Meta:
        verbose_name = _('Medicine')
        verbose_name_plural = _('Medicines')
    
    def __str__(self):
        return self.name

class HealthVisit(models.Model):
    """Health visit model for clinic"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='health_visits', 
                               verbose_name=_('Student'))
    visit_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Visit Date'))
    symptoms = models.TextField(verbose_name=_('Symptoms'))
    diagnosis = models.TextField(blank=True, verbose_name=_('Diagnosis'))
    treatment = models.TextField(blank=True, verbose_name=_('Treatment'))
    attended_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, 
                                   related_name='attended_health_visits', verbose_name=_('Attended By'))
    follow_up_date = models.DateField(null=True, blank=True, verbose_name=_('Follow-up Date'))
    
    class Meta:
        verbose_name = _('Health Visit')
        verbose_name_plural = _('Health Visits')
        ordering = ['-visit_date']
    
    def __str__(self):
        return f"{self.student} - {self.visit_date}"

class MedicineDispensed(models.Model):
    """Medicine dispensed model for health visits"""
    health_visit = models.ForeignKey(HealthVisit, on_delete=models.CASCADE, related_name='medicines_dispensed', 
                                    verbose_name=_('Health Visit'))
    medicine = models.ForeignKey(Medicine, on_delete=models.CASCADE, related_name='dispensed', 
                                verbose_name=_('Medicine'))
    quantity = models.PositiveSmallIntegerField(verbose_name=_('Quantity'))
    dosage = models.CharField(max_length=100, verbose_name=_('Dosage'))
    
    class Meta:
        verbose_name = _('Medicine Dispensed')
        verbose_name_plural = _('Medicines Dispensed')
    
    def __str__(self):
        return f"{self.health_visit.student} - {self.medicine} ({self.quantity})"
    
    def save(self, *args, **kwargs):
        """Override save to update medicine quantity"""
        is_new = self.pk is None
        
        if is_new:
            # Decrease medicine quantity
            self.medicine.quantity -= self.quantity
            self.medicine.save()
        
        super().save(*args, **kwargs)