from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
import os
from accounts.models import User
from students.models import Class, Student
from staff.models import StaffProfile

class Announcement(models.Model):
    """Announcement model"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='announcements', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    target_audience = models.CharField(
        max_length=20,
        choices=[
            ('all', _('All')),
            ('students', _('Students')),
            ('teachers', _('Teachers')),
            ('staff', _('Staff')),
            ('parents', _('Parents'))
        ],
        default='all',
        verbose_name=_('Target Audience')
    )
    specific_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='announcements', verbose_name=_('Specific Class'))
    is_pinned = models.BooleanField(default=False, verbose_name=_('Pinned'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Announcement')
        verbose_name_plural = _('Announcements')
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

def announcement_attachment_path(instance, filename):
    """Generate file path for announcement attachments"""
    return f'announcements/{instance.announcement.id}/{filename}'

class AnnouncementAttachment(models.Model):
    """Announcement attachment model"""
    announcement = models.ForeignKey(Announcement, on_delete=models.CASCADE, related_name='attachments', 
                                    verbose_name=_('Announcement'))
    file = models.FileField(upload_to=announcement_attachment_path, verbose_name=_('File'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))
    
    class Meta:
        verbose_name = _('Announcement Attachment')
        verbose_name_plural = _('Announcement Attachments')
    
    def __str__(self):
        return f"{self.announcement.title} - {self.description}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class Message(models.Model):
    """Private message model"""
    sender = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sent_messages', 
                              verbose_name=_('Sender'))
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='received_messages', 
                                 verbose_name=_('Recipient'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    content = models.TextField(verbose_name=_('Content'))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sent At'))
    read_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Read At'))
    is_read = models.BooleanField(default=False, verbose_name=_('Is Read'))
    parent_message = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='replies', verbose_name=_('Parent Message'))
    
    class Meta:
        verbose_name = _('Message')
        verbose_name_plural = _('Messages')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.sender} to {self.recipient}: {self.subject}"

def message_attachment_path(instance, filename):
    """Generate file path for message attachments"""
    return f'messages/{instance.message.id}/{filename}'

class MessageAttachment(models.Model):
    """Message attachment model"""
    message = models.ForeignKey(Message, on_delete=models.CASCADE, related_name='attachments', 
                               verbose_name=_('Message'))
    file = models.FileField(upload_to=message_attachment_path, verbose_name=_('File'))
    description = models.CharField(max_length=100, blank=True, verbose_name=_('Description'))
    uploaded_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Uploaded At'))
    
    class Meta:
        verbose_name = _('Message Attachment')
        verbose_name_plural = _('Message Attachments')
    
    def __str__(self):
        return f"{self.message.subject} - {self.description}"
    
    @property
    def filename(self):
        return os.path.basename(self.file.name)

class SMSTemplate(models.Model):
    """SMS template model"""
    name = models.CharField(max_length=100, verbose_name=_('Template Name'))
    content = models.TextField(verbose_name=_('Content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='sms_templates', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('SMS Template')
        verbose_name_plural = _('SMS Templates')
    
    def __str__(self):
        return self.name

class EmailTemplate(models.Model):
    """Email template model"""
    name = models.CharField(max_length=100, verbose_name=_('Template Name'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    content = models.TextField(verbose_name=_('Content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='email_templates', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Email Template')
        verbose_name_plural = _('Email Templates')
    
    def __str__(self):
        return self.name

class SMSLog(models.Model):
    """SMS log model"""
    recipient_type = models.CharField(
        max_length=20,
        choices=[
            ('student', _('Student')),
            ('parent', _('Parent')),
            ('teacher', _('Teacher')),
            ('staff', _('Staff')),
            ('other', _('Other'))
        ],
        verbose_name=_('Recipient Type')
    )
    recipient_number = models.CharField(max_length=20, verbose_name=_('Recipient Number'))
    recipient_name = models.CharField(max_length=100, blank=True, verbose_name=_('Recipient Name'))
    content = models.TextField(verbose_name=_('Content'))
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_sms', 
                               verbose_name=_('Sent By'))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sent At'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    gateway_response = models.TextField(blank=True, verbose_name=_('Gateway Response'))
    message_id = models.CharField(max_length=100, blank=True, verbose_name=_('Message ID'))
    
    class Meta:
        verbose_name = _('SMS Log')
        verbose_name_plural = _('SMS Logs')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient_name} ({self.recipient_number}) - {self.sent_at}"

class EmailLog(models.Model):
    """Email log model"""
    recipient_type = models.CharField(
        max_length=20,
        choices=[
            ('student', _('Student')),
            ('parent', _('Parent')),
            ('teacher', _('Teacher')),
            ('staff', _('Staff')),
            ('other', _('Other'))
        ],
        verbose_name=_('Recipient Type')
    )
    recipient_email = models.EmailField(verbose_name=_('Recipient Email'))
    recipient_name = models.CharField(max_length=100, blank=True, verbose_name=_('Recipient Name'))
    subject = models.CharField(max_length=200, verbose_name=_('Subject'))
    content = models.TextField(verbose_name=_('Content'))
    sent_by = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, related_name='sent_emails', 
                               verbose_name=_('Sent By'))
    sent_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Sent At'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('delivered', _('Delivered')),
        ('failed', _('Failed'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    error_message = models.TextField(blank=True, verbose_name=_('Error Message'))
    
    class Meta:
        verbose_name = _('Email Log')
        verbose_name_plural = _('Email Logs')
        ordering = ['-sent_at']
    
    def __str__(self):
        return f"{self.recipient_name} ({self.recipient_email}) - {self.subject}"

class BulkMessage(models.Model):
    """Bulk message model for SMS/Email"""
    message_type = models.CharField(
        max_length=10,
        choices=[
            ('sms', _('SMS')),
            ('email', _('Email'))
        ],
        verbose_name=_('Message Type')
    )
    subject = models.CharField(max_length=200, blank=True, verbose_name=_('Subject'))
    content = models.TextField(verbose_name=_('Content'))
    target_audience = models.CharField(
        max_length=20,
        choices=[
            ('all', _('All')),
            ('students', _('Students')),
            ('teachers', _('Teachers')),
            ('staff', _('Staff')),
            ('parents', _('Parents'))
        ],
        default='all',
        verbose_name=_('Target Audience')
    )
    specific_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='bulk_messages', verbose_name=_('Specific Class'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bulk_messages', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    scheduled_at = models.DateTimeField(null=True, blank=True, verbose_name=_('Scheduled At'))
    
    STATUS_CHOICES = [
        ('draft', _('Draft')),
        ('scheduled', _('Scheduled')),
        ('processing', _('Processing')),
        ('completed', _('Completed')),
        ('failed', _('Failed'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft', 
                             verbose_name=_('Status'))
    total_recipients = models.PositiveIntegerField(default=0, verbose_name=_('Total Recipients'))
    sent_count = models.PositiveIntegerField(default=0, verbose_name=_('Sent Count'))
    failed_count = models.PositiveIntegerField(default=0, verbose_name=_('Failed Count'))
    
    class Meta:
        verbose_name = _('Bulk Message')
        verbose_name_plural = _('Bulk Messages')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.get_message_type_display()} to {self.get_target_audience_display()} - {self.created_at}"

class CalendarEvent(models.Model):
    """Calendar event model"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    start_datetime = models.DateTimeField(verbose_name=_('Start Date/Time'))
    end_datetime = models.DateTimeField(verbose_name=_('End Date/Time'))
    location = models.CharField(max_length=200, blank=True, verbose_name=_('Location'))
    event_type = models.CharField(
        max_length=20,
        choices=[
            ('academic', _('Academic')),
            ('exam', _('Exam')),
            ('holiday', _('Holiday')),
            ('meeting', _('Meeting')),
            ('event', _('Event')),
            ('other', _('Other'))
        ],
        default='other',
        verbose_name=_('Event Type')
    )
    is_all_day = models.BooleanField(default=False, verbose_name=_('All Day Event'))
    is_recurring = models.BooleanField(default=False, verbose_name=_('Recurring Event'))
    recurrence_pattern = models.CharField(max_length=100, blank=True, verbose_name=_('Recurrence Pattern'))
    visibility = models.CharField(
        max_length=20,
        choices=[
            ('public', _('Public')),
            ('staff', _('Staff Only')),
            ('teachers', _('Teachers Only')),
            ('students', _('Students Only')),
            ('parents', _('Parents Only')),
            ('private', _('Private'))
        ],
        default='public',
        verbose_name=_('Visibility')
    )
    specific_class = models.ForeignKey(Class, on_delete=models.SET_NULL, null=True, blank=True, 
                                      related_name='events', verbose_name=_('Specific Class'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_events', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Calendar Event')
        verbose_name_plural = _('Calendar Events')
        ordering = ['start_datetime']
    
    def __str__(self):
        return f"{self.title} ({self.start_datetime.date()})"
    
    @property
    def is_past(self):
        """Check if event is in the past"""
        return timezone.now() > self.end_datetime

class EventAttendee(models.Model):
    """Event attendee model"""
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='attendees', 
                             verbose_name=_('Event'))
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='events', 
                            verbose_name=_('User'))
    
    RESPONSE_CHOICES = [
        ('pending', _('Pending')),
        ('accepted', _('Accepted')),
        ('declined', _('Declined')),
        ('tentative', _('Tentative'))
    ]
    
    response = models.CharField(max_length=20, choices=RESPONSE_CHOICES, default='pending', 
                               verbose_name=_('Response'))
    
    class Meta:
        verbose_name = _('Event Attendee')
        verbose_name_plural = _('Event Attendees')
        unique_together = ('event', 'user')
    
    def __str__(self):
        return f"{self.user} - {self.event}"

class EventReminder(models.Model):
    """Event reminder model"""
    event = models.ForeignKey(CalendarEvent, on_delete=models.CASCADE, related_name='reminders', 
                             verbose_name=_('Event'))
    reminder_time = models.DateTimeField(verbose_name=_('Reminder Time'))
    
    STATUS_CHOICES = [
        ('pending', _('Pending')),
        ('sent', _('Sent')),
        ('failed', _('Failed'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending', 
                             verbose_name=_('Status'))
    
    class Meta:
        verbose_name = _('Event Reminder')
        verbose_name_plural = _('Event Reminders')
        ordering = ['reminder_time']
    
    def __str__(self):
        return f"{self.event} - {self.reminder_time}"

class ParentTeacherMeeting(models.Model):
    """Parent-teacher meeting model"""
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(blank=True, verbose_name=_('Description'))
    date = models.DateField(verbose_name=_('Date'))
    start_time = models.TimeField(verbose_name=_('Start Time'))
    end_time = models.TimeField(verbose_name=_('End Time'))
    location = models.CharField(max_length=200, verbose_name=_('Location'))
    teacher = models.ForeignKey(StaffProfile, on_delete=models.CASCADE, related_name='parent_meetings', 
                               verbose_name=_('Teacher'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='parent_meetings', 
                               verbose_name=_('Student'))
    
    STATUS_CHOICES = [
        ('scheduled', _('Scheduled')),
        ('completed', _('Completed')),
        ('cancelled', _('Cancelled')),
        ('rescheduled', _('Rescheduled'))
    ]
    
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled', 
                             verbose_name=_('Status'))
    notes = models.TextField(blank=True, verbose_name=_('Notes'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_meetings', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Parent-Teacher Meeting')
        verbose_name_plural = _('Parent-Teacher Meetings')
        ordering = ['date', 'start_time']
    
    def __str__(self):
        return f"{self.student} - {self.teacher} ({self.date})"

class Forum(models.Model):
    """Forum model"""
    name = models.CharField(max_length=100, verbose_name=_('Forum Name'))
    description = models.TextField(verbose_name=_('Description'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='created_forums', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Forum')
        verbose_name_plural = _('Forums')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ForumTopic(models.Model):
    """Forum topic model"""
    forum = models.ForeignKey(Forum, on_delete=models.CASCADE, related_name='topics', 
                             verbose_name=_('Forum'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    content = models.TextField(verbose_name=_('Content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_topics', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    is_pinned = models.BooleanField(default=False, verbose_name=_('Pinned'))
    is_closed = models.BooleanField(default=False, verbose_name=_('Closed'))
    
    class Meta:
        verbose_name = _('Forum Topic')
        verbose_name_plural = _('Forum Topics')
        ordering = ['-is_pinned', '-created_at']
    
    def __str__(self):
        return self.title

class ForumReply(models.Model):
    """Forum reply model"""
    topic = models.ForeignKey(ForumTopic, on_delete=models.CASCADE, related_name='replies', 
                             verbose_name=_('Topic'))
    content = models.TextField(verbose_name=_('Content'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='forum_replies', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    updated_at = models.DateTimeField(auto_now=True, verbose_name=_('Updated At'))
    
    class Meta:
        verbose_name = _('Forum Reply')
        verbose_name_plural = _('Forum Replies')
        ordering = ['created_at']
    
    def __str__(self):
        return f"Reply to {self.topic} by {self.created_by}"

class Club(models.Model):
    """Club model"""
    name = models.CharField(max_length=100, verbose_name=_('Club Name'))
    description = models.TextField(verbose_name=_('Description'))
    coordinator = models.ForeignKey(StaffProfile, on_delete=models.SET_NULL, null=True, 
                                   related_name='coordinated_clubs', verbose_name=_('Coordinator'))
    meeting_day = models.CharField(max_length=20, blank=True, verbose_name=_('Meeting Day'))
    meeting_time = models.TimeField(null=True, blank=True, verbose_name=_('Meeting Time'))
    meeting_location = models.CharField(max_length=100, blank=True, verbose_name=_('Meeting Location'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Club')
        verbose_name_plural = _('Clubs')
        ordering = ['name']
    
    def __str__(self):
        return self.name

class ClubMember(models.Model):
    """Club member model"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='members', 
                            verbose_name=_('Club'))
    student = models.ForeignKey(Student, on_delete=models.CASCADE, related_name='clubs', 
                               verbose_name=_('Student'))
    role = models.CharField(max_length=50, blank=True, verbose_name=_('Role'))
    joined_date = models.DateField(auto_now_add=True, verbose_name=_('Joined Date'))
    is_active = models.BooleanField(default=True, verbose_name=_('Active'))
    
    class Meta:
        verbose_name = _('Club Member')
        verbose_name_plural = _('Club Members')
        unique_together = ('club', 'student')
    
    def __str__(self):
        return f"{self.student} - {self.club}"

class ClubActivity(models.Model):
    """Club activity model"""
    club = models.ForeignKey(Club, on_delete=models.CASCADE, related_name='activities', 
                            verbose_name=_('Club'))
    title = models.CharField(max_length=200, verbose_name=_('Title'))
    description = models.TextField(verbose_name=_('Description'))
    date = models.DateField(verbose_name=_('Date'))
    location = models.CharField(max_length=100, blank=True, verbose_name=_('Location'))
    created_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='club_activities', 
                                  verbose_name=_('Created By'))
    created_at = models.DateTimeField(auto_now_add=True, verbose_name=_('Created At'))
    
    class Meta:
        verbose_name = _('Club Activity')
        verbose_name_plural = _('Club Activities')
        ordering = ['-date']
    
    def __str__(self):
        return f"{self.club} - {self.title} ({self.date})"