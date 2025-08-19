from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone
from datetime import datetime, timedelta
from services.models import Service, Therapist, ServiceAddon

User = get_user_model()


class BookingStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    IN_PROGRESS = 'in_progress', 'In Progress'
    COMPLETED = 'completed', 'Completed'
    CANCELLED = 'cancelled', 'Cancelled'
    NO_SHOW = 'no_show', 'No Show'


class Booking(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    booking_date = models.DateField()
    booking_time = models.TimeField()
    end_time = models.TimeField(blank=True, null=True)
    status = models.CharField(max_length=20, choices=BookingStatus.choices, default=BookingStatus.PENDING)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    notes = models.TextField(blank=True, help_text="Special requests or notes")
    is_first_time = models.BooleanField(default=False)
    reminder_sent = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['therapist', 'booking_date', 'booking_time']
        ordering = ['-booking_date', '-booking_time']

    def __str__(self):
        return f"{self.user.email} - {self.service.name} - {self.booking_date} {self.booking_time}"

    def save(self, *args, **kwargs):
        if not self.end_time:
            # Calculate end time based on service duration
            start_datetime = datetime.combine(self.booking_date, self.booking_time)
            end_datetime = start_datetime + timedelta(minutes=self.service.duration)
            self.end_time = end_datetime.time()
        super().save(*args, **kwargs)

    @property
    def duration_minutes(self):
        if self.end_time:
            start_datetime = datetime.combine(self.booking_date, self.booking_time)
            end_datetime = datetime.combine(self.booking_date, self.end_time)
            return (end_datetime - start_datetime).total_seconds() / 60
        return self.service.duration

    @property
    def is_past(self):
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        return timezone.now() > timezone.make_aware(booking_datetime)

    @property
    def can_cancel(self):
        # Can cancel up to 24 hours before appointment
        booking_datetime = datetime.combine(self.booking_date, self.booking_time)
        cancel_deadline = booking_datetime - timedelta(hours=24)
        return timezone.now() < timezone.make_aware(cancel_deadline)


class BookingAddon(models.Model):
    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='addons')
    addon = models.ForeignKey(ServiceAddon, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=8, decimal_places=2)

    def __str__(self):
        return f"{self.booking} - {self.addon.name} x{self.quantity}"

    def save(self, *args, **kwargs):
        if not self.price:
            self.price = self.addon.price
        super().save(*args, **kwargs)


class TimeSlot(models.Model):
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='time_slots')
    date = models.DateField()
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_available = models.BooleanField(default=True)
    is_blocked = models.BooleanField(default=False, help_text="Manually blocked by admin")
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['therapist', 'date', 'start_time']
        ordering = ['date', 'start_time']

    def __str__(self):
        return f"{self.therapist.user.get_full_name()} - {self.date} {self.start_time}-{self.end_time}"

    @property
    def is_past(self):
        slot_datetime = datetime.combine(self.date, self.start_time)
        return timezone.now() > timezone.make_aware(slot_datetime)


class BookingCancellation(models.Model):
    CANCELLATION_REASONS = [
        ('client_request', 'Client Request'),
        ('therapist_unavailable', 'Therapist Unavailable'),
        ('emergency', 'Emergency'),
        ('illness', 'Illness'),
        ('schedule_conflict', 'Schedule Conflict'),
        ('other', 'Other'),
    ]

    booking = models.OneToOneField(Booking, on_delete=models.CASCADE, related_name='cancellation')
    reason = models.CharField(max_length=50, choices=CANCELLATION_REASONS)
    description = models.TextField(blank=True)
    cancelled_by = models.ForeignKey(User, on_delete=models.CASCADE)
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    refund_processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Cancellation for {self.booking}"


class BookingReschedule(models.Model):
    original_booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='reschedules')
    new_date = models.DateField()
    new_time = models.TimeField()
    new_therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, blank=True, null=True)
    reason = models.TextField(blank=True)
    requested_by = models.ForeignKey(User, on_delete=models.CASCADE)
    is_approved = models.BooleanField(default=False)
    approved_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='approved_reschedules', blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Reschedule request for {self.original_booking}"


class RecurringBooking(models.Model):
    FREQUENCY_CHOICES = [
        ('weekly', 'Weekly'),
        ('bi_weekly', 'Bi-weekly'),
        ('monthly', 'Monthly'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='recurring_bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE)
    frequency = models.CharField(max_length=20, choices=FREQUENCY_CHOICES)
    start_date = models.DateField()
    end_date = models.DateField(blank=True, null=True)
    booking_time = models.TimeField()
    is_active = models.BooleanField(default=True)
    total_sessions = models.PositiveIntegerField(blank=True, null=True)
    sessions_completed = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Recurring: {self.user.email} - {self.service.name} ({self.frequency})"

    @property
    def next_booking_date(self):
        if not self.is_active or (self.end_date and timezone.now().date() > self.end_date):
            return None
        
        # Logic to calculate next booking date based on frequency
        # This would need more complex logic based on existing bookings
        return None
