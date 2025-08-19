from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from decimal import Decimal

User = get_user_model()


class PaymentMethod(models.TextChoices):
    MPESA = 'mpesa', 'M-Pesa'
    CARD = 'card', 'Credit/Debit Card'
    BANK_TRANSFER = 'bank_transfer', 'Bank Transfer'
    PAYPAL = 'paypal', 'PayPal'
    CASH = 'cash', 'Cash'


class PaymentStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    PROCESSING = 'processing', 'Processing'
    COMPLETED = 'completed', 'Completed'
    FAILED = 'failed', 'Failed'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'
    PARTIALLY_REFUNDED = 'partially_refunded', 'Partially Refunded'


class Payment(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_id = models.CharField(max_length=100, unique=True)
    
    # Related objects (can be order or appointment)
    order = models.ForeignKey('orders.Order', on_delete=models.CASCADE, blank=True, null=True, related_name='payments')
    service_order = models.ForeignKey('orders.ServiceOrder', on_delete=models.CASCADE, blank=True, null=True, related_name='payments')
    
    # Payment details
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    currency = models.CharField(max_length=3, default='KES')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Payment gateway details
    gateway_transaction_id = models.CharField(max_length=255, blank=True)
    gateway_reference = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # Additional details
    description = models.TextField(blank=True)
    failure_reason = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Payment {self.payment_id} - {self.amount} {self.currency}"

    def save(self, *args, **kwargs):
        if not self.payment_id:
            import uuid
            self.payment_id = f"PAY{str(uuid.uuid4()).upper()[:12]}"
        super().save(*args, **kwargs)

    @property
    def is_successful(self):
        return self.status == PaymentStatus.COMPLETED

    @property
    def can_be_refunded(self):
        return self.status == PaymentStatus.COMPLETED


class PaymentRefund(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE, related_name='refunds')
    refund_id = models.CharField(max_length=100, unique=True)
    amount = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    reason = models.TextField()
    status = models.CharField(max_length=20, choices=PaymentStatus.choices, default=PaymentStatus.PENDING)
    
    # Gateway details
    gateway_refund_id = models.CharField(max_length=255, blank=True)
    gateway_response = models.JSONField(blank=True, null=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"Refund {self.refund_id} - {self.amount} {self.payment.currency}"

    def save(self, *args, **kwargs):
        if not self.refund_id:
            import uuid
            self.refund_id = f"REF{str(uuid.uuid4()).upper()[:12]}"
        super().save(*args, **kwargs)


class MpesaPayment(models.Model):
    """Specific model for M-Pesa payments"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='mpesa_details')
    phone_number = models.CharField(max_length=15)
    merchant_request_id = models.CharField(max_length=100, blank=True)
    checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=100, blank=True)
    transaction_date = models.DateTimeField(blank=True, null=True)
    
    def __str__(self):
        return f"M-Pesa Payment: {self.phone_number} - {self.payment.amount}"


class CardPayment(models.Model):
    """Specific model for card payments"""
    payment = models.OneToOneField(Payment, on_delete=models.CASCADE, related_name='card_details')
    card_brand = models.CharField(max_length=20, blank=True)  # Visa, Mastercard, etc.
    last_four = models.CharField(max_length=4, blank=True)
    expiry_month = models.CharField(max_length=2, blank=True)
    expiry_year = models.CharField(max_length=4, blank=True)
    cardholder_name = models.CharField(max_length=100, blank=True)
    
    def __str__(self):
        return f"Card Payment: ****{self.last_four} - {self.payment.amount}"


class PaymentWebhook(models.Model):
    """Store webhook data from payment gateways"""
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    webhook_id = models.CharField(max_length=100, unique=True)
    event_type = models.CharField(max_length=50)
    data = models.JSONField()
    processed = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Webhook {self.webhook_id} - {self.event_type}"

    def save(self, *args, **kwargs):
        if not self.webhook_id:
            import uuid
            self.webhook_id = f"WH{str(uuid.uuid4()).upper()[:12]}"
        super().save(*args, **kwargs)


class PaymentSettings(models.Model):
    """Store payment gateway configurations"""
    gateway_name = models.CharField(max_length=50, unique=True)
    is_active = models.BooleanField(default=True)
    is_test_mode = models.BooleanField(default=True)
    api_key = models.CharField(max_length=255, blank=True)
    secret_key = models.CharField(max_length=255, blank=True)
    webhook_url = models.URLField(blank=True)
    additional_settings = models.JSONField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Payment Settings"

    def __str__(self):
        return f"{self.gateway_name} Settings"


class PaymentAttempt(models.Model):
    """Track payment attempts for analytics"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payment_attempts')
    payment_method = models.CharField(max_length=20, choices=PaymentMethod.choices)
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    status = models.CharField(max_length=20, choices=PaymentStatus.choices)
    error_message = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    user_agent = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Payment Attempt: {self.user.email} - {self.amount} {self.currency}"
