from rest_framework import serializers
from .models import (
    ServiceCategory, Therapist, Service, ServicePackage, 
    PackageService, ServiceAddon, TherapistAvailability, ServiceReview
)
from accounts.serializers import UserSerializer


class ServiceCategorySerializer(serializers.ModelSerializer):
    services_count = serializers.SerializerMethodField()

    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description', 'image', 'is_active', 'services_count', 'created_at']

    def get_services_count(self, obj):
        return obj.services.filter(is_active=True).count()


class TherapistAvailabilitySerializer(serializers.ModelSerializer):
    day_name = serializers.CharField(source='get_day_of_week_display', read_only=True)

    class Meta:
        model = TherapistAvailability
        fields = ['id', 'day_of_week', 'day_name', 'start_time', 'end_time', 'is_active']


class TherapistSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    specializations = ServiceCategorySerializer(many=True, read_only=True)
    availability = TherapistAvailabilitySerializer(many=True, read_only=True)
    total_reviews = serializers.ReadOnlyField()

    class Meta:
        model = Therapist
        fields = [
            'id', 'user', 'specializations', 'bio', 'experience_years', 
            'rating', 'hourly_rate', 'is_available', 'profile_image', 
            'certifications', 'availability', 'total_reviews', 'created_at'
        ]


class TherapistSimpleSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = Therapist
        fields = ['id', 'name', 'rating', 'profile_image', 'experience_years']


class ServiceAddonSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceAddon
        fields = ['id', 'name', 'description', 'price', 'duration_minutes', 'is_active']


class ServiceReviewSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    therapist = TherapistSimpleSerializer(read_only=True)

    class Meta:
        model = ServiceReview
        fields = ['id', 'user', 'therapist', 'rating', 'comment', 'created_at']


class ServiceSerializer(serializers.ModelSerializer):
    category = ServiceCategorySerializer(read_only=True)
    category_id = serializers.IntegerField(write_only=True)
    therapists = TherapistSimpleSerializer(many=True, read_only=True)
    therapist_ids = serializers.ListField(
        child=serializers.IntegerField(), write_only=True, required=False
    )
    addons = ServiceAddonSerializer(many=True, read_only=True)
    average_rating = serializers.ReadOnlyField()
    total_reviews = serializers.ReadOnlyField()
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)
    reviews = ServiceReviewSerializer(many=True, read_only=True, source='servicereview_set')

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'category', 'category_id', 'description', 'short_description',
            'price', 'duration', 'duration_display', 'therapists', 'therapist_ids',
            'image', 'benefits', 'preparation_notes', 'is_active', 'is_featured',
            'addons', 'average_rating', 'total_reviews', 'reviews', 'created_at'
        ]

    def create(self, validated_data):
        therapist_ids = validated_data.pop('therapist_ids', [])
        service = Service.objects.create(**validated_data)
        if therapist_ids:
            service.therapists.set(therapist_ids)
        return service

    def update(self, instance, validated_data):
        therapist_ids = validated_data.pop('therapist_ids', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        
        if therapist_ids is not None:
            instance.therapists.set(therapist_ids)
        
        return instance


class ServiceSimpleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    duration_display = serializers.CharField(source='get_duration_display', read_only=True)

    class Meta:
        model = Service
        fields = ['id', 'name', 'category_name', 'price', 'duration', 'duration_display', 'image']


class PackageServiceSerializer(serializers.ModelSerializer):
    service = ServiceSimpleSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = PackageService
        fields = ['id', 'service', 'service_id', 'quantity']


class ServicePackageSerializer(serializers.ModelSerializer):
    package_services = PackageServiceSerializer(many=True, read_only=True, source='packageservice_set')
    original_price = serializers.ReadOnlyField()
    savings = serializers.ReadOnlyField()

    class Meta:
        model = ServicePackage
        fields = [
            'id', 'name', 'description', 'price', 'discount_percentage',
            'validity_days', 'image', 'is_active', 'package_services',
            'original_price', 'savings', 'created_at'
        ]


class CreateServiceReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceReview
        fields = ['service', 'therapist', 'rating', 'comment']

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)