from django.contrib import admin
from .models import (
    ServiceCategory, Therapist, Service, ServicePackage, 
    PackageService, ServiceAddon, TherapistAvailability, ServiceReview
)


@admin.register(ServiceCategory)
class ServiceCategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    prepopulated_fields = {'name': ('name',)}


class TherapistAvailabilityInline(admin.TabularInline):
    model = TherapistAvailability
    extra = 0


@admin.register(Therapist)
class TherapistAdmin(admin.ModelAdmin):
    list_display = ['user', 'experience_years', 'rating', 'hourly_rate', 'is_available']
    list_filter = ['is_available', 'experience_years', 'specializations', 'created_at']
    search_fields = ['user__first_name', 'user__last_name', 'user__email', 'bio']
    filter_horizontal = ['specializations']
    inlines = [TherapistAvailabilityInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'level', 'price', 'duration', 'is_active', 'is_featured']
    list_filter = ['category', 'level', 'duration', 'is_active', 'is_featured', 'created_at']
    search_fields = ['name', 'description', 'short_description']
    filter_horizontal = ['therapists']
    list_editable = ['is_active', 'is_featured']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'category', 'level', 'short_description', 'description')
        }),
        ('Pricing & Duration', {
            'fields': ('price', 'duration')
        }),
        ('Service Details', {
            'fields': ('benefits', 'preparation_notes', 'image')
        }),
        ('Therapists & Status', {
            'fields': ('therapists', 'is_active', 'is_featured')
        }),
    )


class PackageServiceInline(admin.TabularInline):
    model = PackageService
    extra = 0


@admin.register(ServicePackage)
class ServicePackageAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'discount_percentage', 'validity_days', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    inlines = [PackageServiceInline]
    list_editable = ['is_active']


@admin.register(ServiceAddon)
class ServiceAddonAdmin(admin.ModelAdmin):
    list_display = ['name', 'price', 'duration_minutes', 'is_active']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'description']
    filter_horizontal = ['services']
    list_editable = ['is_active']


@admin.register(TherapistAvailability)
class TherapistAvailabilityAdmin(admin.ModelAdmin):
    list_display = ['therapist', 'get_day_of_week_display', 'start_time', 'end_time', 'is_active']
    list_filter = ['day_of_week', 'is_active', 'therapist']
    search_fields = ['therapist__user__first_name', 'therapist__user__last_name']
    list_editable = ['is_active']


@admin.register(ServiceReview)
class ServiceReviewAdmin(admin.ModelAdmin):
    list_display = ['service', 'user', 'therapist', 'rating', 'created_at']
    list_filter = ['rating', 'created_at', 'service__category']
    search_fields = ['service__name', 'user__email', 'therapist__user__first_name', 'comment']
    readonly_fields = ['created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('service', 'user', 'therapist__user')