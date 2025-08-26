from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import Booking, BookingStatus

@receiver(post_save, sender=Booking)
def send_booking_email(sender, instance, created, **kwargs):
    # Only send email if booking is created or status changed to completed
    if created or (instance.status == BookingStatus.COMPLETED):
        subject = f"New Booking Completed: {instance.service.name} for {instance.user.get_full_name()}"
        message = f"Booking Details:\n\n" \
                  f"User: {instance.user.get_full_name()} ({instance.user.email})\n" \
                  f"Service: {instance.service.name}\n" \
                  f"Therapist: {instance.therapist.user.get_full_name()}\n" \
                  f"Date: {instance.booking_date}\n" \
                  f"Time: {instance.booking_time}\n" \
                  f"Status: {instance.get_status_display()}\n" \
                  f"Total Amount: {instance.total_amount}\n" \
                  f"Notes: {instance.notes}\n"
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            ['thelaydiesden@gmail.com'],
            fail_silently=False,
        )
