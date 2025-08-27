from django.db import models
from django.utils.translation import gettext_lazy as _
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
import os
from accounts.models import User
from students.models import Class, Student

class Subject(models.Model):
    """Subject model"""
    name = models.CharField(max_length=100, verbose_name=_('Subject Name'))
    code = models.CharField(max_length=20, unique=True, verbose_name=_('Subject Code'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    credit_hours = models.PositiveSmallIntegerField(default=1, verbose_name=_('Credit Hours'))
    is_elective = models.BooleanField(default=False, verbose_name=_('Is Elective'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Subject')
        verbose_name_plural = _('Subjects')
    
    def __str__(self):
        return f"{self.code} - {self.name}"

class ClassSubject(models.Model):
    """Class-Subject relationship model"""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='subjects', verbose_name=_('Class'))
    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name='classes', verbose_name=_('Subject'))
    teacher = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='teaching_subjects', verbose_name=_('Teacher'))
    passing_marks = models.DecimalField(max_digits=5, decimal_places=2, default=40.00, verbose_name=_('Passing Marks'))
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, verbose_name=_('Maximum Marks'))
    
    class Meta:
        verbose_name = _('Class Subject')
        verbose_name_plural = _('Class Subjects')
        unique_together = ('class_obj', 'subject')
    
    def __str__(self):
        return f"{self.class_obj} - {self.subject}"

class ExamType(models.Model):
    """Exam type model"""
    name = models.CharField(max_length=100, verbose_name=_('Exam Type'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    weight = models.PositiveSmallIntegerField(default=100, validators=[MinValueValidator(1), MaxValueValidator(100)], 
                                             verbose_name=_('Weight Percentage'))
    
    class Meta:
        verbose_name = _('Exam Type')
        verbose_name_plural = _('Exam Types')
    
    def __str__(self):
        return self.name

class Exam(models.Model):
    """Exam model"""
    name = models.CharField(max_length=100, verbose_name=_('Exam Name'))
    exam_type = models.ForeignKey(ExamType, on_delete=models.CASCADE, related_name='exams', verbose_name=_('Exam Type'))
    start_date = models.DateField(verbose_name=_('Start Date'))
    end_date = models.DateField(verbose_name=_('End Date'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Exam')
        verbose_name_plural = _('Exams')
    
    def __str__(self):
        return f"{self.name} ({self.academic_year})"

class ExamSchedule(models.Model):
    """Exam schedule model"""
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='schedules', verbose_name=_('Exam'))
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='exam_schedules', 
                                     verbose_name=_('Subject'))
    date = models.DateField(verbose_name=_('Exam Date'))
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    venue = models.CharField(max_length=100, verbose_name=_('Venue'))
    invigilator = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='invigilation_duties',
                                   verbose_name=_('Invigilator'))
    
    class Meta:
        verbose_name = _('Exam Schedule')
        verbose_name_plural = _('Exam Schedules')
        unique_together = ('exam', 'class_subject', 'date')
    
    def __str__(self):
        return f"{self.class_subject.subject} - {self.date} ({self.start_time} to {self.end_time})"

class Grade(models.Model):
    """Grade model for exam results"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='grades', verbose_name=_('Student'))
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='grades', verbose_name=_('Subject'))
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='grades', verbose_name=_('Exam'))
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Marks Obtained'))
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Maximum Marks'))
    grade_letter = models.CharField(max_length=2, blank=True, verbose_name=_('Grade Letter'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    date_recorded = models.DateField(auto_now_add=True, verbose_name=_('Date Recorded'))
    
    class Meta:
        verbose_name = _('Grade')
        verbose_name_plural = _('Grades')
        unique_together = ('student', 'class_subject', 'exam')
    
    def __str__(self):
        return f"{self.student} - {self.class_subject.subject} - {self.exam}"
    
    def calculate_percentage(self):
        """Calculate percentage of marks"""
        if self.max_marks > 0:
            return (self.marks_obtained / self.max_marks) * 100
        return 0
    
    def save(self, *args, **kwargs):
        """Override save to automatically calculate grade letter"""
        percentage = self.calculate_percentage()
        
        # Define grade boundaries
        if percentage >= 90:
            self.grade_letter = 'A+'
        elif percentage >= 80:
            self.grade_letter = 'A'
        elif percentage >= 70:
            self.grade_letter = 'B+'
        elif percentage >= 60:
            self.grade_letter = 'B'
        elif percentage >= 50:
            self.grade_letter = 'C+'
        elif percentage >= 40:
            self.grade_letter = 'C'
        elif percentage >= 33:
            self.grade_letter = 'D'
        else:
            self.grade_letter = 'F'
            
        super().save(*args, **kwargs)

class GradeScale(models.Model):
    """Grade scale model for defining grading system"""
    name = models.CharField(max_length=50, verbose_name=_('Scale Name'))
    min_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Minimum Percentage'))
    max_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Maximum Percentage'))
    grade_letter = models.CharField(max_length=2, verbose_name=_('Grade Letter'))
    grade_point = models.DecimalField(max_digits=3, decimal_places=2, verbose_name=_('Grade Point'))
    description = models.CharField(max_length=50, blank=True, verbose_name=_('Description'))
    
    class Meta:
        verbose_name = _('Grade Scale')
        verbose_name_plural = _('Grade Scales')
        ordering = ['-min_percentage']
    
    def __str__(self):
        return f"{self.grade_letter} ({self.min_percentage}% - {self.max_percentage}%)"

class GPA(models.Model):
    """GPA model for tracking student GPA"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='gpas', verbose_name=_('Student'))
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='gpas', verbose_name=_('Class'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    term = models.CharField(max_length=20, verbose_name=_('Term'))
    gpa = models.DecimalField(max_digits=3, decimal_places=2, verbose_name=_('GPA'))
    total_credits = models.PositiveSmallIntegerField(verbose_name=_('Total Credits'))
    date_calculated = models.DateField(auto_now=True, verbose_name=_('Date Calculated'))
    
    class Meta:
        verbose_name = _('GPA')
        verbose_name_plural = _('GPAs')
        unique_together = ('student', 'class_obj', 'academic_year', 'term')
    
    def __str__(self):
        return f"{self.student} - {self.academic_year} {self.term} - GPA: {self.gpa}"

def assignment_file_path(instance, filename):
    """Generate file path for assignment files"""
    return f'assignments/{instance.class_subject.class_obj.id}/{instance.id}/{filename}'

class Assignment(models.Model):
    """Assignment model"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='assignments', 
                                     verbose_name=_('Subject'))
    assigned_date = models.DateField(auto_now_add=True, verbose_name=_('Assigned Date'))
    due_date = models.DateField(verbose_name=_('Due Date'))
    max_marks = models.DecimalField(max_digits=5, decimal_places=2, default=100.00, verbose_name=_('Maximum Marks'))
    weight_percentage = models.PositiveSmallIntegerField(default=10, validators=[MinValueValidator(1), MaxValueValidator(100)], 
                                                       verbose_name=_('Weight Percentage'))
    file = models.FileField(upload_to=assignment_file_path, blank=True, null=True, verbose_name=_('Assignment File'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Assignment')
        verbose_name_plural = _('Assignments')
        ordering = ['-due_date']
    
    def __str__(self):
        return f"{self.title} - {self.class_subject}"
    
    @property
    def is_past_due(self):
        return timezone.now().date() > self.due_date

def submission_file_path(instance, filename):
    """Generate file path for submission files"""
    return f'submissions/{instance.assignment.class_subject.class_obj.id}/{instance.assignment.id}/{instance.student.id}/{filename}'

class AssignmentSubmission(models.Model):
    """Assignment submission model"""
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE, related_name='submissions', 
                                  verbose_name=_('Assignment'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='submissions', 
                               verbose_name=_('Student'))
    submission_date = models.DateTimeField(auto_now_add=True, verbose_name=_('Submission Date'))
    file = models.FileField(upload_to=submission_file_path, verbose_name=_('Submission File'))
    remarks = models.TextField(blank=True, verbose_name=_('Remarks'))
    marks_obtained = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                        verbose_name=_('Marks Obtained'))
    is_graded = models.BooleanField(default=False, verbose_name=_('Is Graded'))
    
    class Meta:
        verbose_name = _('Assignment Submission')
        verbose_name_plural = _('Assignment Submissions')
        unique_together = ('assignment', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.assignment}"
    
    @property
    def is_late(self):
        return self.submission_date.date() > self.assignment.due_date
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class TimeSlot(models.Model):
    """Time slot model for timetable"""
    name = models.CharField(max_length=50, verbose_name=_('Slot Name'))
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    
    class Meta:
        verbose_name = _('Time Slot')
        verbose_name_plural = _('Time Slots')
        ordering = ['start_time']
    
    def __str__(self):
        return f"{self.name} ({self.start_time} - {self.end_time})"

class WeekDay(models.Model):
    """Weekday model for timetable"""
    name = models.CharField(max_length=20, verbose_name=_('Day Name'))
    order = models.PositiveSmallIntegerField(unique=True, verbose_name=_('Order'))
    is_weekend = models.BooleanField(default=False, verbose_name=_('Is Weekend'))
    
    class Meta:
        verbose_name = _('Week Day')
        verbose_name_plural = _('Week Days')
        ordering = ['order']
    
    def __str__(self):
        return self.name

class Timetable(models.Model):
    """Timetable model"""
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='timetables', verbose_name=_('Class'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    term = models.CharField(max_length=20, verbose_name=_('Term'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Timetable')
        verbose_name_plural = _('Timetables')
        unique_together = ('class_obj', 'academic_year', 'term')
    
    def __str__(self):
        return f"{self.class_obj} - {self.academic_year} {self.term}"

class TimetableEntry(models.Model):
    """Timetable entry model"""
    timetable = models.ForeignKey(Timetable, on_delete=models.CASCADE, related_name='entries', verbose_name=_('Timetable'))
    day = models.ForeignKey(WeekDay, on_delete=models.CASCADE, related_name='timetable_entries', verbose_name=_('Day'))
    time_slot = models.ForeignKey(TimeSlot, on_delete=models.CASCADE, related_name='timetable_entries', 
                                 verbose_name=_('Time Slot'))
    class_subject = models.ForeignKey(ClassSubject, on_delete=models.CASCADE, related_name='timetable_entries', 
                                     verbose_name=_('Subject'))
    room = models.CharField(max_length=50, verbose_name=_('Room'))
    
    class Meta:
        verbose_name = _('Timetable Entry')
        verbose_name_plural = _('Timetable Entries')
        unique_together = ('timetable', 'day', 'time_slot')
    
    def __str__(self):
        return f"{self.timetable.class_obj} - {self.day} - {self.time_slot} - {self.class_subject.subject}"

class ReportCard(models.Model):
    """Report card model"""
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='report_cards', verbose_name=_('Student'))
    class_obj = models.ForeignKey(Class, on_delete=models.CASCADE, related_name='report_cards', verbose_name=_('Class'))
    academic_year = models.CharField(max_length=20, verbose_name=_('Academic Year'))
    term = models.CharField(max_length=20, verbose_name=_('Term'))
    exam = models.ForeignKey(Exam, on_delete=models.CASCADE, related_name='report_cards', verbose_name=_('Exam'))
    total_marks = models.DecimalField(max_digits=6, decimal_places=2, verbose_name=_('Total Marks'))
    average_percentage = models.DecimalField(max_digits=5, decimal_places=2, verbose_name=_('Average Percentage'))
    rank = models.PositiveIntegerField(null=True, blank=True, verbose_name=_('Rank'))
    gpa = models.DecimalField(max_digits=3, decimal_places=2, null=True, blank=True, verbose_name=_('GPA'))
    attendance_percentage = models.DecimalField(max_digits=5, decimal_places=2, null=True, blank=True, 
                                              verbose_name=_('Attendance Percentage'))
    teacher_remarks = models.TextField(blank=True, verbose_name=_('Teacher Remarks'))
    principal_remarks = models.TextField(blank=True, verbose_name=_('Principal Remarks'))
    generated_date = models.DateField(auto_now_add=True, verbose_name=_('Generated Date'))
    
    class Meta:
        verbose_name = _('Report Card')
        verbose_name_plural = _('Report Cards')
        unique_together = ('student', 'class_obj', 'academic_year', 'term', 'exam')
    
    def __str__(self):
        return f"{self.student} - {self.class_obj} - {self.term} {self.academic_year}"