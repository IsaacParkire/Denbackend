from django.contrib import admin
from .models import (
    Order, OrderItem, ServiceOrder, OrderTracking, 
    OrderRefund, Coupon
)


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['total_price']


class OrderTrackingInline(admin.TabularInline):
    model = OrderTracking
    extra = 0
    readonly_fields = ['created_at']


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'status', 'total_amount', 
        'payment_status', 'created_at'
    ]
    list_filter = [
        'status', 'payment_status', 'payment_method', 'created_at',
        'shipping_country'
    ]
    search_fields = [
        'order_number', 'user__email', 'user__first_name', 'user__last_name',
        'shipping_email', 'billing_email'
    ]
    readonly_fields = [
        'order_number', 'full_shipping_address', 'total_items',
        'created_at', 'updated_at'
    ]
    list_editable = ['status', 'payment_status']
    inlines = [OrderItemInline, OrderTrackingInline]
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Order Information', {
            'fields': ('user', 'order_number', 'status', 'payment_status', 'payment_method')
        }),
        ('Pricing', {
            'fields': ('subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount')
        }),
        ('Shipping Address', {
            'fields': (
                'shipping_first_name', 'shipping_last_name', 'shipping_email', 'shipping_phone',
                'shipping_address_line_1', 'shipping_address_line_2',
                'shipping_city', 'shipping_state', 'shipping_postal_code', 'shipping_country'
            )
        }),
        ('Billing Address', {
            'fields': (
                'billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone',
                'billing_address_line_1', 'billing_address_line_2',
                'billing_city', 'billing_state', 'billing_postal_code', 'billing_country'
            ),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('notes', 'full_shipping_address', 'total_items'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'shipped_at', 'delivered_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = ['order', 'product', 'variant', 'quantity', 'unit_price', 'total_price']
    list_filter = ['order__status', 'product__category']
    search_fields = ['order__order_number', 'product__name', 'variant__name']
    readonly_fields = ['total_price']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'order', 'product', 'variant'
        )


@admin.register(ServiceOrder)
class ServiceOrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number', 'user', 'service', 'appointment_date', 
        'appointment_time', 'status', 'total_amount'
    ]
    list_filter = ['status', 'appointment_date', 'service__category']
    search_fields = [
        'order_number', 'user__email', 'service__name'
    ]
    readonly_fields = ['order_number', 'created_at', 'updated_at']
    date_hierarchy = 'appointment_date'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user', 'service')


@admin.register(OrderTracking)
class OrderTrackingAdmin(admin.ModelAdmin):
    list_display = ['order', 'status', 'description', 'location', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['order__order_number', 'description', 'tracking_number']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(OrderRefund)
class OrderRefundAdmin(admin.ModelAdmin):
    list_display = [
        'order', 'reason', 'refund_amount', 'is_approved', 
        'is_processed', 'created_at'
    ]
    list_filter = ['reason', 'is_approved', 'is_processed', 'created_at']
    search_fields = ['order__order_number', 'description']
    readonly_fields = ['created_at']
    list_editable = ['is_approved', 'is_processed']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('order')


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code', 'discount_type', 'discount_value', 'usage_limit',
        'used_count', 'is_active', 'valid_from', 'valid_until'
    ]
    list_filter = ['discount_type', 'is_active', 'valid_from', 'valid_until']
    search_fields = ['code']
    readonly_fields = ['used_count', 'is_valid', 'created_at']
    list_editable = ['is_active']
    date_hierarchy = 'valid_from'
