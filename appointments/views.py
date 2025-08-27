from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import (
    Booking, BookingAddon, TimeSlot, BookingCancellation, 
    BookingReschedule, RecurringBooking, BookingStatus
)
from .serializers import (
    BookingSerializer, CreateBookingSerializer, TimeSlotSerializer,
    BookingCancellationSerializer, BookingRescheduleSerializer,
    RecurringBookingSerializer, AvailableTimeSlotsSerializer,
    BookingStatsSerializer
)
from services.models import Therapist, Service


class BookingListView(generics.ListCreateAPIView):
    permission_classes = []  # Allow any (guests and authenticated)
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'therapist', 'booking_date']
    search_fields = ['service__name', 'therapist__user__first_name', 'therapist__user__last_name']
    ordering_fields = ['booking_date', 'booking_time', 'created_at']
    ordering = ['-booking_date', '-booking_time']

    def get_queryset(self):
        if self.request.user.is_authenticated:
            return Booking.objects.filter(user=self.request.user)
        return Booking.objects.none()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateBookingSerializer
        return BookingSerializer

    def perform_create(self, serializer):
        if self.request.user.is_authenticated:
            serializer.save(user=self.request.user)
        else:
            serializer.save(user=None)  # Or handle guest bookings as needed


class BookingDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = BookingSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Booking.objects.filter(user=self.request.user)


class AllBookingsView(generics.ListAPIView):
    """Admin view to see all bookings"""
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'therapist', 'booking_date', 'user']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'service__name', 'therapist__user__first_name', 'therapist__user__last_name'
    ]
    ordering_fields = ['booking_date', 'booking_time', 'created_at']
    ordering = ['-booking_date', '-booking_time']


class TimeSlotListView(generics.ListCreateAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['therapist', 'date', 'is_available', 'is_blocked']
    ordering_fields = ['date', 'start_time']
    ordering = ['date', 'start_time']


class TimeSlotDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TimeSlot.objects.all()
    serializer_class = TimeSlotSerializer


class BookingCancellationListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reason', 'refund_processed']
    ordering = ['-created_at']

    def get_queryset(self):
        return BookingCancellation.objects.filter(cancelled_by=self.request.user)

    def get_serializer_class(self):
        return BookingCancellationSerializer


class BookingRescheduleListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['is_approved']
    ordering = ['-created_at']

    def get_queryset(self):
        return BookingReschedule.objects.filter(requested_by=self.request.user)

    def get_serializer_class(self):
        return BookingRescheduleSerializer


class RecurringBookingListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['frequency', 'is_active']
    ordering = ['-created_at']

    def get_queryset(self):
        return RecurringBooking.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return RecurringBookingSerializer


@api_view(['GET'])
def available_time_slots(request):
    """
    Get available time slots for a specific therapist, date, and service
    """
    serializer = AvailableTimeSlotsSerializer(data=request.query_params)
    if not serializer.is_valid():
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    date = serializer.validated_data['date']
    therapist_id = serializer.validated_data['therapist_id']
    service_id = serializer.validated_data['service_id']
    
    try:
        therapist = Therapist.objects.get(id=therapist_id)
        service = Service.objects.get(id=service_id)
    except (Therapist.DoesNotExist, Service.DoesNotExist):
        return Response({'error': 'Therapist or Service not found'}, status=404)
    
    # Get therapist availability for the day
    day_of_week = date.weekday()
    availability = therapist.availability.filter(
        day_of_week=day_of_week,
        is_active=True
    )
    
    if not availability.exists():
        return Response({'available_slots': []})
    
    # Generate time slots based on availability
    available_slots = []
    for avail in availability:
        current_time = avail.start_time
        end_time = avail.end_time
        
        while current_time < end_time:
            # Check if slot duration fits
            slot_end = (datetime.combine(date, current_time) + 
                       timedelta(minutes=service.duration)).time()
            
            if slot_end <= end_time:
                # Check if slot is not already booked
                existing_booking = Booking.objects.filter(
                    therapist=therapist,
                    booking_date=date,
                    booking_time=current_time,
                    status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
                ).exists()
                
                # Check if slot is not blocked
                blocked_slot = TimeSlot.objects.filter(
                    therapist=therapist,
                    date=date,
                    start_time=current_time,
                    is_blocked=True
                ).exists()
                
                if not existing_booking and not blocked_slot:
                    available_slots.append({
                        'time': current_time.strftime('%H:%M'),
                        'end_time': slot_end.strftime('%H:%M')
                    })
            
            # Move to next 30-minute slot
            current_time = (datetime.combine(date, current_time) + 
                           timedelta(minutes=30)).time()
    
    return Response({'available_slots': available_slots})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_booking(request, booking_id):
    """
    Cancel a booking
    """
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)
    
    if not booking.can_cancel:
        return Response(
            {'error': 'Booking cannot be cancelled (less than 24 hours notice)'},
            status=400
        )
    
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        return Response({'error': 'Booking is already cancelled or completed'}, status=400)
    
    # Create cancellation record
    reason = request.data.get('reason', 'client_request')
    description = request.data.get('description', '')
    
    cancellation = BookingCancellation.objects.create(
        booking=booking,
        reason=reason,
        description=description,
        cancelled_by=request.user,
        refund_amount=booking.total_amount  # Full refund for 24+ hours notice
    )
    
    # Update booking status
    booking.status = BookingStatus.CANCELLED
    booking.save()
    
    return Response({'message': 'Booking cancelled successfully'})


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def reschedule_booking(request, booking_id):
    """
    Request to reschedule a booking
    """
    try:
        booking = Booking.objects.get(id=booking_id, user=request.user)
    except Booking.DoesNotExist:
        return Response({'error': 'Booking not found'}, status=404)
    
    if booking.status in [BookingStatus.CANCELLED, BookingStatus.COMPLETED]:
        return Response({'error': 'Cannot reschedule cancelled or completed booking'}, status=400)
    
    serializer = BookingRescheduleSerializer(data=request.data, context={'request': request})
    if serializer.is_valid():
        serializer.save(original_booking=booking)
        return Response(serializer.data, status=201)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_booking_stats(request):
    """
    Get booking statistics for the current user
    """
    user_bookings = Booking.objects.filter(user=request.user)
    
    stats = {
        'total_bookings': user_bookings.count(),
        'pending_bookings': user_bookings.filter(status=BookingStatus.PENDING).count(),
        'confirmed_bookings': user_bookings.filter(status=BookingStatus.CONFIRMED).count(),
        'completed_bookings': user_bookings.filter(status=BookingStatus.COMPLETED).count(),
        'cancelled_bookings': user_bookings.filter(status=BookingStatus.CANCELLED).count(),
        'total_spent': user_bookings.filter(
            status=BookingStatus.COMPLETED
        ).aggregate(total=Sum('total_amount'))['total'] or 0
    }
    
    return Response(stats)


@api_view(['GET'])
def therapist_schedule(request, therapist_id):
    """
    Get therapist's schedule for a specific date range
    """
    try:
        therapist = Therapist.objects.get(id=therapist_id)
    except Therapist.DoesNotExist:
        return Response({'error': 'Therapist not found'}, status=404)
    
    start_date = request.query_params.get('start_date')
    end_date = request.query_params.get('end_date')
    
    if not start_date or not end_date:
        return Response({'error': 'start_date and end_date are required'}, status=400)
    
    try:
        start_date = datetime.strptime(start_date, '%Y-%m-%d').date()
        end_date = datetime.strptime(end_date, '%Y-%m-%d').date()
    except ValueError:
        return Response({'error': 'Invalid date format. Use YYYY-MM-DD'}, status=400)
    
    bookings = Booking.objects.filter(
        therapist=therapist,
        booking_date__range=[start_date, end_date],
        status__in=[BookingStatus.PENDING, BookingStatus.CONFIRMED]
    )
    
    serializer = BookingSerializer(bookings, many=True)
    return Response({
        'therapist': therapist.user.get_full_name(),
        'schedule': serializer.data
    })


@api_view(['GET'])
def booking_dashboard_stats(request):
    """
    Get overall booking statistics (admin view)
    """
    today = timezone.now().date()
    
    stats = {
        'total_bookings': Booking.objects.count(),
        'today_bookings': Booking.objects.filter(booking_date=today).count(),
        'pending_bookings': Booking.objects.filter(status=BookingStatus.PENDING).count(),
        'confirmed_bookings': Booking.objects.filter(status=BookingStatus.CONFIRMED).count(),
        'completed_bookings': Booking.objects.filter(status=BookingStatus.COMPLETED).count(),
        'cancelled_bookings': Booking.objects.filter(status=BookingStatus.CANCELLED).count(),
        'total_revenue': Booking.objects.filter(
            status=BookingStatus.COMPLETED
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'this_month_revenue': Booking.objects.filter(
            status=BookingStatus.COMPLETED,
            booking_date__month=today.month,
            booking_date__year=today.year
        ).aggregate(total=Sum('total_amount'))['total'] or 0
    }
    
    return Response(stats)
