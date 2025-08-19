from django.contrib import admin
from .models import (
    Booking, BookingAddon, TimeSlot, BookingCancellation, 
    BookingReschedule, RecurringBooking
)


class BookingAddonInline(admin.TabularInline):
    model = BookingAddon
    extra = 0


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'service', 'therapist', 'booking_date', 'booking_time', 
        'status', 'total_amount', 'created_at'
    ]
    list_filter = [
        'status', 'booking_date', 'service__category', 'therapist', 
        'is_first_time', 'created_at'
    ]
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'service__name', 'therapist__user__first_name', 'therapist__user__last_name'
    ]
    date_hierarchy = 'booking_date'
    list_editable = ['status']
    inlines = [BookingAddonInline]
    
    fieldsets = (
        ('Booking Information', {
            'fields': ('user', 'service', 'therapist', 'booking_date', 'booking_time', 'end_time')
        }),
        ('Status & Payment', {
            'fields': ('status', 'total_amount', 'is_first_time')
        }),
        ('Additional Information', {
            'fields': ('notes', 'reminder_sent'),
            'classes': ('collapse',)
        }),
    )
    
    readonly_fields = ['end_time', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'service', 'therapist__user'
        )


@admin.register(TimeSlot)
class TimeSlotAdmin(admin.ModelAdmin):
    list_display = ['therapist', 'date', 'start_time', 'end_time', 'is_available', 'is_blocked']
    list_filter = ['is_available', 'is_blocked', 'date', 'therapist']
    search_fields = ['therapist__user__first_name', 'therapist__user__last_name']
    date_hierarchy = 'date'
    list_editable = ['is_available', 'is_blocked']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('therapist__user')


@admin.register(BookingCancellation)
class BookingCancellationAdmin(admin.ModelAdmin):
    list_display = [
        'booking', 'reason', 'cancelled_by', 'refund_amount', 
        'refund_processed', 'created_at'
    ]
    list_filter = ['reason', 'refund_processed', 'created_at']
    search_fields = [
        'booking__user__email', 'cancelled_by__email', 'description'
    ]
    readonly_fields = ['created_at']
    list_editable = ['refund_processed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'booking__user', 'cancelled_by'
        )


@admin.register(BookingReschedule)
class BookingRescheduleAdmin(admin.ModelAdmin):
    list_display = [
        'original_booking', 'new_date', 'new_time', 'new_therapist',
        'is_approved', 'requested_by', 'created_at'
    ]
    list_filter = ['is_approved', 'new_date', 'created_at']
    search_fields = [
        'original_booking__user__email', 'requested_by__email', 'reason'
    ]
    readonly_fields = ['created_at', 'processed_at']
    list_editable = ['is_approved']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'original_booking__user', 'requested_by', 'new_therapist__user'
        )


@admin.register(RecurringBooking)
class RecurringBookingAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'service', 'therapist', 'frequency', 'start_date', 
        'end_date', 'is_active', 'sessions_completed'
    ]
    list_filter = ['frequency', 'is_active', 'start_date', 'service__category']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'service__name', 'therapist__user__first_name'
    ]
    date_hierarchy = 'start_date'
    list_editable = ['is_active']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'service', 'therapist__user'
        )
