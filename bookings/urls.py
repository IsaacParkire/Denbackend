from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    # Bookings
    path('', views.BookingListView.as_view(), name='booking-list'),
    path('<int:pk>/', views.BookingDetailView.as_view(), name='booking-detail'),
    path('all/', views.AllBookingsView.as_view(), name='all-bookings'),
    
    # Booking Actions
    path('<int:booking_id>/cancel/', views.cancel_booking, name='cancel-booking'),
    path('<int:booking_id>/reschedule/', views.reschedule_booking, name='reschedule-booking'),
    
    # Time Slots
    path('time-slots/', views.TimeSlotListView.as_view(), name='timeslot-list'),
    path('time-slots/<int:pk>/', views.TimeSlotDetailView.as_view(), name='timeslot-detail'),
    path('available-slots/', views.available_time_slots, name='available-slots'),
    
    # Cancellations
    path('cancellations/', views.BookingCancellationListView.as_view(), name='cancellation-list'),
    
    # Reschedules
    path('reschedules/', views.BookingRescheduleListView.as_view(), name='reschedule-list'),
    
    # Recurring Bookings
    path('recurring/', views.RecurringBookingListView.as_view(), name='recurring-booking-list'),
    
    # Statistics and Reports
    path('stats/', views.user_booking_stats, name='user-stats'),
    path('dashboard-stats/', views.booking_dashboard_stats, name='dashboard-stats'),
    
    # Therapist Schedule
    path('therapist/<int:therapist_id>/schedule/', views.therapist_schedule, name='therapist-schedule'),
]
