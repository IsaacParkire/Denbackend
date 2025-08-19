from rest_framework import serializers
from .models import (
    Payment, PaymentRefund, MpesaPayment, CardPayment, 
    PaymentWebhook, PaymentAttempt
)
from accounts.serializers import UserSerializer


class PaymentSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    is_successful = serializers.ReadOnlyField()
    can_be_refunded = serializers.ReadOnlyField()

    class Meta:
        model = Payment
        fields = [
            'id', 'user', 'payment_id', 'order', 'service_order',
            'amount', 'currency', 'payment_method', 'payment_method_display',
            'status', 'status_display', 'gateway_transaction_id', 'gateway_reference',
            'description', 'failure_reason', 'is_successful', 'can_be_refunded',
            'created_at', 'updated_at', 'completed_at'
        ]
        read_only_fields = [
            'payment_id', 'gateway_transaction_id', 'gateway_reference',
            'gateway_response', 'created_at', 'updated_at', 'completed_at'
        ]


class CreatePaymentSerializer(serializers.ModelSerializer):
    class Meta:
        model = Payment
        fields = [
            'order', 'service_order', 'amount', 'currency', 
            'payment_method', 'description'
        ]

    def validate(self, data):
        # Ensure either order or service_order is provided, but not both
        order = data.get('order')
        service_order = data.get('service_order')
        
        if not order and not service_order:
            raise serializers.ValidationError(
                "Either order or service_order must be provided"
            )
        
        if order and service_order:
            raise serializers.ValidationError(
                "Cannot specify both order and service_order"
            )
        
        return data

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class MpesaPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = MpesaPayment
        fields = [
            'id', 'payment', 'phone_number', 'merchant_request_id',
            'checkout_request_id', 'mpesa_receipt_number', 'transaction_date'
        ]


class InitiateMpesaPaymentSerializer(serializers.Serializer):
    phone_number = serializers.CharField(max_length=15)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.IntegerField(required=False)
    service_order_id = serializers.IntegerField(required=False)
    description = serializers.CharField(max_length=255, required=False)

    def validate_phone_number(self, value):
        # Basic phone number validation for Kenyan numbers
        if not value.startswith(('254', '+254', '07', '01')):
            raise serializers.ValidationError(
                "Please enter a valid Kenyan phone number"
            )
        return value

    def validate(self, data):
        order_id = data.get('order_id')
        service_order_id = data.get('service_order_id')
        
        if not order_id and not service_order_id:
            raise serializers.ValidationError(
                "Either order_id or service_order_id must be provided"
            )
        
        if order_id and service_order_id:
            raise serializers.ValidationError(
                "Cannot specify both order_id and service_order_id"
            )
        
        return data


class CardPaymentSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)

    class Meta:
        model = CardPayment
        fields = [
            'id', 'payment', 'card_brand', 'last_four',
            'expiry_month', 'expiry_year', 'cardholder_name'
        ]


class InitiateCardPaymentSerializer(serializers.Serializer):
    card_number = serializers.CharField(max_length=19, write_only=True)
    expiry_month = serializers.CharField(max_length=2)
    expiry_year = serializers.CharField(max_length=4)
    cvv = serializers.CharField(max_length=4, write_only=True)
    cardholder_name = serializers.CharField(max_length=100)
    amount = serializers.DecimalField(max_digits=10, decimal_places=2)
    order_id = serializers.IntegerField(required=False)
    service_order_id = serializers.IntegerField(required=False)

    def validate_card_number(self, value):
        # Remove spaces and validate length
        card_number = value.replace(' ', '')
        if len(card_number) < 13 or len(card_number) > 19:
            raise serializers.ValidationError("Invalid card number length")
        return card_number

    def validate(self, data):
        order_id = data.get('order_id')
        service_order_id = data.get('service_order_id')
        
        if not order_id and not service_order_id:
            raise serializers.ValidationError(
                "Either order_id or service_order_id must be provided"
            )
        
        return data


class PaymentRefundSerializer(serializers.ModelSerializer):
    payment = PaymentSerializer(read_only=True)
    payment_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentRefund
        fields = [
            'id', 'payment', 'payment_id', 'refund_id', 'amount', 'reason',
            'status', 'status_display', 'gateway_refund_id',
            'created_at', 'processed_at'
        ]
        read_only_fields = ['refund_id', 'gateway_refund_id', 'created_at', 'processed_at']


class PaymentWebhookSerializer(serializers.ModelSerializer):
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)

    class Meta:
        model = PaymentWebhook
        fields = [
            'id', 'payment_method', 'payment_method_display', 'webhook_id',
            'event_type', 'data', 'processed', 'created_at'
        ]


class PaymentAttemptSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    payment_method_display = serializers.CharField(source='get_payment_method_display', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = PaymentAttempt
        fields = [
            'id', 'user', 'payment_method', 'payment_method_display',
            'amount', 'currency', 'status', 'status_display',
            'error_message', 'ip_address', 'created_at'
        ]


class PaymentStatsSerializer(serializers.Serializer):
    total_payments = serializers.IntegerField()
    successful_payments = serializers.IntegerField()
    failed_payments = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    total_refunds = serializers.IntegerField()
    refund_amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class PaymentMethodStatsSerializer(serializers.Serializer):
    payment_method = serializers.CharField()
    count = serializers.IntegerField()
    total_amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    success_rate = serializers.DecimalField(max_digits=5, decimal_places=2)
