from django.urls import path
from . import views

app_name = 'services'

urlpatterns = [
    # Service Categories
    path('categories/', views.ServiceCategoryListView.as_view(), name='category-list'),
    path('categories/<int:pk>/', views.ServiceCategoryDetailView.as_view(), name='category-detail'),
    path('categories-with-services/', views.service_categories_with_services, name='categories-with-services'),
    
    # Therapists
    path('therapists/', views.TherapistListView.as_view(), name='therapist-list'),
    path('therapists/<int:pk>/', views.TherapistDetailView.as_view(), name='therapist-detail'),
    path('therapists/<int:therapist_id>/services/', views.therapist_services, name='therapist-services'),
    
    # Services
    path('', views.ServiceListView.as_view(), name='service-list'),
    path('<int:pk>/', views.ServiceDetailView.as_view(), name='service-detail'),
    path('featured/', views.FeaturedServicesView.as_view(), name='featured-services'),
    path('search/', views.service_search, name='service-search'),
    
    # Service Packages
    path('packages/', views.ServicePackageListView.as_view(), name='package-list'),
    path('packages/<int:pk>/', views.ServicePackageDetailView.as_view(), name='package-detail'),
    
    # Service Addons
    path('addons/', views.ServiceAddonListView.as_view(), name='addon-list'),
    path('addons/<int:pk>/', views.ServiceAddonDetailView.as_view(), name='addon-detail'),
    
    # Therapist Availability
    path('availability/', views.TherapistAvailabilityListView.as_view(), name='availability-list'),
    path('availability/<int:pk>/', views.TherapistAvailabilityDetailView.as_view(), name='availability-detail'),
    
    # Service Reviews
    path('reviews/', views.ServiceReviewListView.as_view(), name='review-list'),
    path('reviews/<int:pk>/', views.ServiceReviewDetailView.as_view(), name='review-detail'),
    path('my-reviews/', views.user_service_reviews, name='user-reviews'),
]