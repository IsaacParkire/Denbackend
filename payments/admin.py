from django.contrib import admin
from .models import (
    Payment, PaymentRefund, MpesaPayment, CardPayment,
    PaymentWebhook, PaymentSettings, PaymentAttempt
)


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment_id', 'user', 'amount', 'currency', 'payment_method',
        'status', 'created_at', 'completed_at'
    ]
    list_filter = [
        'status', 'payment_method', 'currency', 'created_at'
    ]
    search_fields = [
        'payment_id', 'user__email', 'gateway_transaction_id',
        'gateway_reference', 'description'
    ]
    readonly_fields = [
        'payment_id', 'gateway_response', 'is_successful', 'can_be_refunded',
        'created_at', 'updated_at', 'completed_at'
    ]
    list_editable = ['status']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Payment Information', {
            'fields': ('user', 'payment_id', 'order', 'service_order')
        }),
        ('Amount & Method', {
            'fields': ('amount', 'currency', 'payment_method', 'status')
        }),
        ('Gateway Details', {
            'fields': ('gateway_transaction_id', 'gateway_reference', 'gateway_response'),
            'classes': ('collapse',)
        }),
        ('Additional Information', {
            'fields': ('description', 'failure_reason'),
            'classes': ('collapse',)
        }),
        ('Status Checks', {
            'fields': ('is_successful', 'can_be_refunded'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at', 'completed_at'),
            'classes': ('collapse',)
        }),
    )
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(PaymentRefund)
class PaymentRefundAdmin(admin.ModelAdmin):
    list_display = [
        'refund_id', 'payment', 'amount', 'status', 'created_at', 'processed_at'
    ]
    list_filter = ['status', 'created_at', 'processed_at']
    search_fields = ['refund_id', 'payment__payment_id', 'reason']
    readonly_fields = ['refund_id', 'created_at', 'processed_at']
    list_editable = ['status']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment__user')


@admin.register(MpesaPayment)
class MpesaPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'phone_number', 'mpesa_receipt_number', 
        'transaction_date', 'payment_status'
    ]
    list_filter = ['payment__status', 'transaction_date']
    search_fields = [
        'phone_number', 'mpesa_receipt_number', 'merchant_request_id',
        'checkout_request_id', 'payment__payment_id'
    ]
    readonly_fields = ['transaction_date']
    
    def payment_status(self, obj):
        return obj.payment.status
    payment_status.short_description = 'Payment Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')


@admin.register(CardPayment)
class CardPaymentAdmin(admin.ModelAdmin):
    list_display = [
        'payment', 'card_brand', 'last_four', 'cardholder_name', 'payment_status'
    ]
    list_filter = ['payment__status', 'card_brand']
    search_fields = [
        'last_four', 'cardholder_name', 'payment__payment_id'
    ]
    
    def payment_status(self, obj):
        return obj.payment.status
    payment_status.short_description = 'Payment Status'
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('payment')


@admin.register(PaymentWebhook)
class PaymentWebhookAdmin(admin.ModelAdmin):
    list_display = [
        'webhook_id', 'payment_method', 'event_type', 'processed', 'created_at'
    ]
    list_filter = ['payment_method', 'event_type', 'processed', 'created_at']
    search_fields = ['webhook_id', 'event_type']
    readonly_fields = ['webhook_id', 'created_at']
    list_editable = ['processed']


@admin.register(PaymentSettings)
class PaymentSettingsAdmin(admin.ModelAdmin):
    list_display = [
        'gateway_name', 'is_active', 'is_test_mode', 'created_at', 'updated_at'
    ]
    list_filter = ['is_active', 'is_test_mode']
    search_fields = ['gateway_name']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_active', 'is_test_mode']


@admin.register(PaymentAttempt)
class PaymentAttemptAdmin(admin.ModelAdmin):
    list_display = [
        'user', 'payment_method', 'amount', 'currency', 'status', 'created_at'
    ]
    list_filter = ['payment_method', 'status', 'currency', 'created_at']
    search_fields = ['user__email', 'error_message', 'ip_address']
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')
