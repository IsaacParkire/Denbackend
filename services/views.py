from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Avg
from .models import (
    ServiceCategory, Therapist, Service, ServicePackage, 
    ServiceAddon, TherapistAvailability, ServiceReview
)
from .serializers import (
    ServiceCategorySerializer, TherapistSerializer, ServiceSerializer,
    ServicePackageSerializer, ServiceAddonSerializer, 
    TherapistAvailabilitySerializer, ServiceReviewSerializer,
    CreateServiceReviewSerializer, TherapistSimpleSerializer
)


class ServiceCategoryListView(generics.ListCreateAPIView):
    queryset = ServiceCategory.objects.filter(is_active=True)
    serializer_class = ServiceCategorySerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'created_at']
    ordering = ['name']


class ServiceCategoryDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer


class TherapistListView(generics.ListCreateAPIView):
    queryset = Therapist.objects.filter(is_available=True)
    serializer_class = TherapistSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['specializations', 'experience_years']
    search_fields = ['user__first_name', 'user__last_name', 'bio', 'certifications']
    ordering_fields = ['rating', 'experience_years', 'created_at']
    ordering = ['-rating']


class TherapistDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Therapist.objects.all()
    serializer_class = TherapistSerializer


class ServiceListView(generics.ListCreateAPIView):
    queryset = Service.objects.filter(is_active=True)
    serializer_class = ServiceSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'duration', 'is_featured', 'therapists']
    search_fields = ['name', 'description', 'short_description', 'benefits']
    ordering_fields = ['name', 'price', 'duration', 'created_at']
    ordering = ['name']

    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by price range
        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        
        if min_price:
            queryset = queryset.filter(price__gte=min_price)
        if max_price:
            queryset = queryset.filter(price__lte=max_price)
            
        # Filter by category name
        category_name = self.request.query_params.get('category_name')
        if category_name:
            queryset = queryset.filter(category__name__icontains=category_name)
            
        return queryset


class ServiceDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Service.objects.all()
    serializer_class = ServiceSerializer


class FeaturedServicesView(generics.ListAPIView):
    queryset = Service.objects.filter(is_active=True, is_featured=True)
    serializer_class = ServiceSerializer
    ordering = ['-created_at']


class ServicePackageListView(generics.ListCreateAPIView):
    queryset = ServicePackage.objects.filter(is_active=True)
    serializer_class = ServicePackageSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['name']


class ServicePackageDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServicePackage.objects.all()
    serializer_class = ServicePackageSerializer


class ServiceAddonListView(generics.ListCreateAPIView):
    queryset = ServiceAddon.objects.filter(is_active=True)
    serializer_class = ServiceAddonSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['name', 'description']
    ordering_fields = ['name', 'price']
    ordering = ['name']


class ServiceAddonDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceAddon.objects.all()
    serializer_class = ServiceAddonSerializer


class TherapistAvailabilityListView(generics.ListCreateAPIView):
    serializer_class = TherapistAvailabilitySerializer
    filter_backends = [DjangoFilterBackend]
    filterset_fields = ['therapist', 'day_of_week', 'is_active']

    def get_queryset(self):
        return TherapistAvailability.objects.filter(is_active=True)


class TherapistAvailabilityDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = TherapistAvailability.objects.all()
    serializer_class = TherapistAvailabilitySerializer


class ServiceReviewListView(generics.ListCreateAPIView):
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['service', 'therapist', 'rating']
    ordering_fields = ['rating', 'created_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return ServiceReview.objects.all()

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateServiceReviewSerializer
        return ServiceReviewSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return [IsAuthenticatedOrReadOnly()]


class ServiceReviewDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = ServiceReview.objects.all()
    serializer_class = ServiceReviewSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return CreateServiceReviewSerializer
        return ServiceReviewSerializer


@api_view(['GET'])
def service_search(request):
    """
    Advanced service search with multiple filters
    """
    query = request.GET.get('q', '')
    category = request.GET.get('category')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    duration = request.GET.get('duration')
    therapist = request.GET.get('therapist')
    
    services = Service.objects.filter(is_active=True)
    
    if query:
        services = services.filter(
            Q(name__icontains=query) |
            Q(description__icontains=query) |
            Q(short_description__icontains=query) |
            Q(category__name__icontains=query)
        )
    
    if category:
        services = services.filter(category_id=category)
    
    if min_price:
        services = services.filter(price__gte=min_price)
    
    if max_price:
        services = services.filter(price__lte=max_price)
    
    if duration:
        services = services.filter(duration=duration)
    
    if therapist:
        services = services.filter(therapists=therapist)
    
    serializer = ServiceSerializer(services, many=True)
    return Response(serializer.data)


@api_view(['GET'])
def therapist_services(request, therapist_id):
    """
    Get all services provided by a specific therapist
    """
    try:
        therapist = Therapist.objects.get(id=therapist_id)
        services = therapist.services.filter(is_active=True)
        serializer = ServiceSerializer(services, many=True)
        return Response(serializer.data)
    except Therapist.DoesNotExist:
        return Response({'error': 'Therapist not found'}, status=404)


@api_view(['GET'])
def service_categories_with_services(request):
    """
    Get all categories with their services
    """
    categories = ServiceCategory.objects.filter(is_active=True).prefetch_related('services')
    data = []
    
    for category in categories:
        services = category.services.filter(is_active=True)
        category_data = ServiceCategorySerializer(category).data
        category_data['services'] = ServiceSerializer(services, many=True).data
        data.append(category_data)
    
    return Response(data)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_service_reviews(request):
    """
    Get all reviews by the current user
    """
    reviews = ServiceReview.objects.filter(user=request.user)
    serializer = ServiceReviewSerializer(reviews, many=True)
    return Response(serializer.data)