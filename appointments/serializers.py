from rest_framework import serializers
from .models import (
    Booking, BookingAddon, TimeSlot, BookingCancellation, 
    BookingReschedule, RecurringBooking
)
from services.serializers import ServiceSimpleSerializer, TherapistSimpleSerializer, ServiceAddonSerializer
from accounts.serializers import UserSerializer


class BookingAddonSerializer(serializers.ModelSerializer):
    addon = ServiceAddonSerializer(read_only=True)
    addon_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = BookingAddon
        fields = ['id', 'addon', 'addon_id', 'quantity', 'price']


class BookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSimpleSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    therapist = TherapistSimpleSerializer(read_only=True)
    therapist_id = serializers.IntegerField(write_only=True)
    addons = BookingAddonSerializer(many=True, read_only=True)
    duration_minutes = serializers.ReadOnlyField()
    is_past = serializers.ReadOnlyField()
    can_cancel = serializers.ReadOnlyField()
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Booking
        fields = [
            'id', 'user', 'service', 'service_id', 'therapist', 'therapist_id',
            'booking_date', 'booking_time', 'end_time', 'status', 'status_display',
            'total_amount', 'notes', 'is_first_time', 'reminder_sent',
            'addons', 'duration_minutes', 'is_past', 'can_cancel',
            'created_at', 'updated_at'
        ]
        read_only_fields = ['end_time', 'created_at', 'updated_at']

    def validate(self, data):
        # Check if the time slot is available
        booking_date = data.get('booking_date')
        booking_time = data.get('booking_time')
        therapist_id = data.get('therapist_id')
        
        if booking_date and booking_time and therapist_id:
            # Check for existing bookings at the same time
            existing_booking = Booking.objects.filter(
                therapist_id=therapist_id,
                booking_date=booking_date,
                booking_time=booking_time
            ).exclude(id=self.instance.id if self.instance else None)
            
            if existing_booking.exists():
                raise serializers.ValidationError(
                    "This time slot is already booked for the selected therapist."
                )
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CreateBookingSerializer(serializers.ModelSerializer):
    addon_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )

    class Meta:
        model = Booking
        fields = [
            'service_id', 'therapist_id', 'booking_date', 'booking_time',
            'notes', 'addon_ids'
        ]

    def create(self, validated_data):
        addon_ids = validated_data.pop('addon_ids', [])
        validated_data['user'] = self.context['request'].user
        
        # Calculate total amount
        from services.models import Service, ServiceAddon
        service = Service.objects.get(id=validated_data['service_id'])
        total_amount = service.price
        
        if addon_ids:
            addons = ServiceAddon.objects.filter(id__in=addon_ids)
            total_amount += sum(addon.price for addon in addons)
        
        validated_data['total_amount'] = total_amount
        booking = Booking.objects.create(**validated_data)
        
        # Create booking addons
        if addon_ids:
            for addon_id in addon_ids:
                addon = ServiceAddon.objects.get(id=addon_id)
                BookingAddon.objects.create(
                    booking=booking,
                    addon=addon,
                    price=addon.price
                )
        
        return booking


class TimeSlotSerializer(serializers.ModelSerializer):
    therapist = TherapistSimpleSerializer(read_only=True)
    therapist_id = serializers.IntegerField(write_only=True)
    is_past = serializers.ReadOnlyField()

    class Meta:
        model = TimeSlot
        fields = [
            'id', 'therapist', 'therapist_id', 'date', 'start_time', 'end_time',
            'is_available', 'is_blocked', 'is_past', 'created_at'
        ]


class BookingCancellationSerializer(serializers.ModelSerializer):
    booking = BookingSerializer(read_only=True)
    booking_id = serializers.IntegerField(write_only=True)
    cancelled_by = UserSerializer(read_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = BookingCancellation
        fields = [
            'id', 'booking', 'booking_id', 'reason', 'reason_display',
            'description', 'cancelled_by', 'refund_amount', 'refund_processed',
            'created_at'
        ]

    def create(self, validated_data):
        validated_data['cancelled_by'] = self.context['request'].user
        return super().create(validated_data)


class BookingRescheduleSerializer(serializers.ModelSerializer):
    original_booking = BookingSerializer(read_only=True)
    original_booking_id = serializers.IntegerField(write_only=True)
    new_therapist = TherapistSimpleSerializer(read_only=True)
    new_therapist_id = serializers.IntegerField(write_only=True, required=False)
    requested_by = UserSerializer(read_only=True)
    approved_by = UserSerializer(read_only=True)

    class Meta:
        model = BookingReschedule
        fields = [
            'id', 'original_booking', 'original_booking_id', 'new_date', 'new_time',
            'new_therapist', 'new_therapist_id', 'reason', 'requested_by',
            'is_approved', 'approved_by', 'created_at', 'processed_at'
        ]

    def create(self, validated_data):
        validated_data['requested_by'] = self.context['request'].user
        return super().create(validated_data)


class RecurringBookingSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSimpleSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    therapist = TherapistSimpleSerializer(read_only=True)
    therapist_id = serializers.IntegerField(write_only=True)
    frequency_display = serializers.CharField(source='get_frequency_display', read_only=True)
    next_booking_date = serializers.ReadOnlyField()

    class Meta:
        model = RecurringBooking
        fields = [
            'id', 'user', 'service', 'service_id', 'therapist', 'therapist_id',
            'frequency', 'frequency_display', 'start_date', 'end_date',
            'booking_time', 'is_active', 'total_sessions', 'sessions_completed',
            'next_booking_date', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class AvailableTimeSlotsSerializer(serializers.Serializer):
    date = serializers.DateField()
    therapist_id = serializers.IntegerField()
    service_id = serializers.IntegerField()


class BookingStatsSerializer(serializers.Serializer):
    total_bookings = serializers.IntegerField()
    pending_bookings = serializers.IntegerField()
    confirmed_bookings = serializers.IntegerField()
    completed_bookings = serializers.IntegerField()
    cancelled_bookings = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=10, decimal_places=2)
