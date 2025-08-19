from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator
from products.models import Product, ProductVariant
from services.models import Service

User = get_user_model()


class OrderStatus(models.TextChoices):
    PENDING = 'pending', 'Pending'
    CONFIRMED = 'confirmed', 'Confirmed'
    PROCESSING = 'processing', 'Processing'
    SHIPPED = 'shipped', 'Shipped'
    DELIVERED = 'delivered', 'Delivered'
    CANCELLED = 'cancelled', 'Cancelled'
    REFUNDED = 'refunded', 'Refunded'


class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    order_number = models.CharField(max_length=50, unique=True)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    # Pricing
    subtotal = models.DecimalField(max_digits=10, decimal_places=2)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    shipping_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    discount_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Shipping Information
    shipping_first_name = models.CharField(max_length=100)
    shipping_last_name = models.CharField(max_length=100)
    shipping_email = models.EmailField()
    shipping_phone = models.CharField(max_length=20)
    shipping_address_line_1 = models.CharField(max_length=255)
    shipping_address_line_2 = models.CharField(max_length=255, blank=True)
    shipping_city = models.CharField(max_length=100)
    shipping_state = models.CharField(max_length=100)
    shipping_postal_code = models.CharField(max_length=20)
    shipping_country = models.CharField(max_length=100, default='Kenya')
    
    # Billing Information (can be same as shipping)
    billing_first_name = models.CharField(max_length=100)
    billing_last_name = models.CharField(max_length=100)
    billing_email = models.EmailField()
    billing_phone = models.CharField(max_length=20)
    billing_address_line_1 = models.CharField(max_length=255)
    billing_address_line_2 = models.CharField(max_length=255, blank=True)
    billing_city = models.CharField(max_length=100)
    billing_state = models.CharField(max_length=100)
    billing_postal_code = models.CharField(max_length=20)
    billing_country = models.CharField(max_length=100, default='Kenya')
    
    # Additional Information
    notes = models.TextField(blank=True, help_text="Order notes")
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    shipped_at = models.DateTimeField(blank=True, null=True)
    delivered_at = models.DateTimeField(blank=True, null=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order {self.order_number} - {self.user.email}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"LD{str(uuid.uuid4()).upper()[:8]}"
        super().save(*args, **kwargs)

    @property
    def full_shipping_address(self):
        address_parts = [
            self.shipping_address_line_1,
            self.shipping_address_line_2,
            self.shipping_city,
            self.shipping_state,
            self.shipping_postal_code,
            self.shipping_country
        ]
        return ', '.join(filter(None, address_parts))

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(validators=[MinValueValidator(1)])
    unit_price = models.DecimalField(max_digits=10, decimal_places=2)
    total_price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"{self.product.name}{variant_str} x{self.quantity}"

    def save(self, *args, **kwargs):
        if not self.unit_price:
            self.unit_price = self.variant.price if self.variant else self.product.price
        self.total_price = self.unit_price * self.quantity
        super().save(*args, **kwargs)


class ServiceOrder(models.Model):
    """Orders specifically for services/appointments"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='service_orders')
    order_number = models.CharField(max_length=50, unique=True)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    status = models.CharField(max_length=20, choices=OrderStatus.choices, default=OrderStatus.PENDING)
    
    # Pricing
    service_price = models.DecimalField(max_digits=10, decimal_places=2)
    addons_price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    tax_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    
    # Service Details
    appointment_date = models.DateField()
    appointment_time = models.TimeField()
    duration_minutes = models.PositiveIntegerField()
    special_requests = models.TextField(blank=True)
    
    # Payment Information
    payment_method = models.CharField(max_length=50, blank=True)
    payment_status = models.CharField(max_length=50, default='pending')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Service Order {self.order_number} - {self.service.name}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            import uuid
            self.order_number = f"SLD{str(uuid.uuid4()).upper()[:8]}"
        super().save(*args, **kwargs)


class OrderTracking(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='tracking')
    status = models.CharField(max_length=20, choices=OrderStatus.choices)
    description = models.TextField()
    location = models.CharField(max_length=255, blank=True)
    tracking_number = models.CharField(max_length=100, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Tracking: {self.order.order_number} - {self.status}"


class OrderRefund(models.Model):
    REFUND_REASONS = [
        ('defective', 'Defective Product'),
        ('wrong_item', 'Wrong Item Received'),
        ('not_as_described', 'Not as Described'),
        ('changed_mind', 'Changed Mind'),
        ('damaged_shipping', 'Damaged During Shipping'),
        ('other', 'Other'),
    ]

    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='refunds')
    reason = models.CharField(max_length=50, choices=REFUND_REASONS)
    description = models.TextField()
    refund_amount = models.DecimalField(max_digits=10, decimal_places=2)
    is_approved = models.BooleanField(default=False)
    is_processed = models.BooleanField(default=False)
    processed_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Refund: {self.order.order_number} - ${self.refund_amount}"


class Coupon(models.Model):
    DISCOUNT_TYPES = [
        ('percentage', 'Percentage'),
        ('fixed', 'Fixed Amount'),
    ]

    code = models.CharField(max_length=50, unique=True)
    discount_type = models.CharField(max_length=20, choices=DISCOUNT_TYPES)
    discount_value = models.DecimalField(max_digits=10, decimal_places=2)
    minimum_order_amount = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    maximum_discount_amount = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    usage_limit = models.PositiveIntegerField(blank=True, null=True)
    used_count = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    valid_from = models.DateTimeField()
    valid_until = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Coupon: {self.code}"

    @property
    def is_valid(self):
        from django.utils import timezone
        now = timezone.now()
        return (
            self.is_active and
            self.valid_from <= now <= self.valid_until and
            (self.usage_limit is None or self.used_count < self.usage_limit)
        )

    def calculate_discount(self, order_amount):
        if not self.is_valid or order_amount < self.minimum_order_amount:
            return 0

        if self.discount_type == 'percentage':
            discount = order_amount * (self.discount_value / 100)
            if self.maximum_discount_amount:
                discount = min(discount, self.maximum_discount_amount)
        else:
            discount = self.discount_value

        return min(discount, order_amount)
