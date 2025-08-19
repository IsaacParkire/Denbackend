from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from django.utils.html import format_html
from .models import User, UserProfile, MembershipPlan, MembershipHistory

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = (
        'email', 
        'first_name', 
        'last_name', 
        'membership_type_display',
        'membership_status_display',
        'membership_active_display',
        'is_staff', 
        'is_active', 
        'date_joined'
    )
    list_filter = (
        'membership_type',
        'membership_status', 
        'is_staff', 
        'is_active', 
        'date_joined', 
        'last_login'
    )
    search_fields = ('email', 'first_name', 'last_name', 'phone_number')
    ordering = ('-date_joined',)
    
    fieldsets = (
        (None, {'fields': ('email', 'password')}),
        (_('Personal info'), {
            'fields': ('first_name', 'last_name', 'phone_number', 'date_of_birth', 'gender', 'address')
        }),
        (_('Membership'), {
            'fields': (
                'membership_type', 
                'membership_status', 
                'membership_start_date', 
                'membership_end_date'
            ),
            'classes': ('collapse',),
        }),
        (_('Permissions'), {
            'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions'),
        }),
        (_('Important dates'), {'fields': ('last_login', 'date_joined')}),
    )
    
    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('email', 'password1', 'password2', 'first_name', 'last_name', 'membership_type'),
        }),
    )
    
    readonly_fields = ('date_joined', 'last_login')
    
    def membership_type_display(self, obj):
        colors = {
            'basic': '#6B7280',  # Gray
            'premium': '#F59E0B',  # Yellow
            'vip': '#8B5CF6',  # Purple
        }
        color = colors.get(obj.membership_type, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.membership_display_name
        )
    membership_type_display.short_description = 'Membership Type'
    
    def membership_status_display(self, obj):
        colors = {
            'active': '#10B981',  # Green
            'expired': '#EF4444',  # Red
            'cancelled': '#6B7280',  # Gray
            'pending': '#F59E0B',  # Yellow
        }
        color = colors.get(obj.membership_status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_membership_status_display()
        )
    membership_status_display.short_description = 'Status'
    
    def membership_active_display(self, obj):
        if obj.is_membership_active:
            return format_html('<span style="color: #10B981;">✓ Active</span>')
        else:
            return format_html('<span style="color: #EF4444;">✗ Inactive</span>')
    membership_active_display.short_description = 'Active Status'

@admin.register(UserProfile)
class UserProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'preferred_services', 'loyalty_points', 'vip_member', 'created_at')
    list_filter = ('vip_member', 'created_at')
    search_fields = ('user__email', 'user__first_name', 'user__last_name')
    readonly_fields = ('created_at', 'updated_at')

@admin.register(MembershipPlan)
class MembershipPlanAdmin(admin.ModelAdmin):
    list_display = (
        'name', 
        'plan_type', 
        'price_display', 
        'duration_months', 
        'features_count',
        'is_active'
    )
    list_filter = ('plan_type', 'is_active', 'created_at')
    search_fields = ('name', 'description')
    readonly_fields = ('created_at', 'updated_at')
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'plan_type', 'price', 'currency', 'duration_months', 'description')
        }),
        ('Features & Access', {
            'fields': (
                'her_secrets_access',
                'premium_events_access', 
                'vip_events_access',
                'priority_booking',
                'premium_gallery_access',
                'vip_gallery_access',
                'custom_experiences',
                'concierge_service',
                'private_events'
            ),
            'classes': ('collapse',),
        }),
        ('Feature Lists', {
            'fields': ('features_list', 'restrictions_list'),
            'classes': ('collapse',),
        }),
        ('Status', {
            'fields': ('is_active',)
        }),
    )
    
    def price_display(self, obj):
        return f"{obj.currency} {obj.price:,.2f}"
    price_display.short_description = 'Price'
    
    def features_count(self, obj):
        return len(obj.features_list) if obj.features_list else 0
    features_count.short_description = 'Features'

@admin.register(MembershipHistory)
class MembershipHistoryAdmin(admin.ModelAdmin):
    list_display = (
        'user',
        'plan', 
        'status_display',
        'start_date',
        'end_date',
        'payment_amount_display',
        'payment_date'
    )
    list_filter = ('status', 'plan__plan_type', 'payment_date', 'auto_renew')
    search_fields = (
        'user__email', 
        'user__first_name', 
        'user__last_name',
        'payment_reference'
    )
    readonly_fields = ('created_at', 'updated_at')
    date_hierarchy = 'payment_date'
    
    fieldsets = (
        ('Membership Info', {
            'fields': ('user', 'plan', 'status', 'start_date', 'end_date', 'auto_renew')
        }),
        ('Payment Info', {
            'fields': ('payment_amount', 'payment_method', 'payment_reference', 'payment_date'),
            'classes': ('collapse',),
        }),
    )
    
    def status_display(self, obj):
        colors = {
            'pending': '#F59E0B',  # Yellow
            'active': '#10B981',   # Green
            'expired': '#EF4444',  # Red
            'cancelled': '#6B7280', # Gray
            'refunded': '#8B5CF6',  # Purple
        }
        color = colors.get(obj.status, '#6B7280')
        return format_html(
            '<span style="color: {}; font-weight: bold;">{}</span>',
            color,
            obj.get_status_display()
        )
    status_display.short_description = 'Status'
    
    def payment_amount_display(self, obj):
        return f"KSH {obj.payment_amount:,.2f}"
    payment_amount_display.short_description = 'Amount'
