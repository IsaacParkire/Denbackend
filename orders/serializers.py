from rest_framework import serializers
from .models import (
    Order, OrderItem, ServiceOrder, OrderTracking, 
    OrderRefund, Coupon
)
from products.serializers import ProductSimpleSerializer, ProductVariantSerializer
from services.serializers import ServiceSimpleSerializer
from accounts.serializers import UserSerializer


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = OrderItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'unit_price', 'total_price'
        ]


class OrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    full_shipping_address = serializers.ReadOnlyField()
    total_items = serializers.ReadOnlyField()

    class Meta:
        model = Order
        fields = [
            'id', 'user', 'order_number', 'status', 'status_display',
            'subtotal', 'tax_amount', 'shipping_amount', 'discount_amount', 'total_amount',
            'shipping_first_name', 'shipping_last_name', 'shipping_email', 'shipping_phone',
            'shipping_address_line_1', 'shipping_address_line_2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone',
            'billing_address_line_1', 'billing_address_line_2', 'billing_city',
            'billing_state', 'billing_postal_code', 'billing_country',
            'notes', 'payment_method', 'payment_status',
            'items', 'full_shipping_address', 'total_items',
            'created_at', 'updated_at', 'shipped_at', 'delivered_at'
        ]


class CreateOrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True)

    class Meta:
        model = Order
        fields = [
            'shipping_first_name', 'shipping_last_name', 'shipping_email', 'shipping_phone',
            'shipping_address_line_1', 'shipping_address_line_2', 'shipping_city',
            'shipping_state', 'shipping_postal_code', 'shipping_country',
            'billing_first_name', 'billing_last_name', 'billing_email', 'billing_phone',
            'billing_address_line_1', 'billing_address_line_2', 'billing_city',
            'billing_state', 'billing_postal_code', 'billing_country',
            'notes', 'payment_method', 'items'
        ]

    def create(self, validated_data):
        items_data = validated_data.pop('items')
        validated_data['user'] = self.context['request'].user
        
        # Calculate totals
        subtotal = 0
        for item_data in items_data:
            from products.models import Product, ProductVariant
            product = Product.objects.get(id=item_data['product_id'])
            variant_id = item_data.get('variant_id')
            variant = ProductVariant.objects.get(id=variant_id) if variant_id else None
            
            unit_price = variant.price if variant else product.price
            quantity = item_data['quantity']
            subtotal += unit_price * quantity
        
        # For now, simple calculation (you can add tax and shipping logic)
        validated_data['subtotal'] = subtotal
        validated_data['total_amount'] = subtotal
        
        order = Order.objects.create(**validated_data)
        
        # Create order items
        for item_data in items_data:
            OrderItem.objects.create(order=order, **item_data)
        
        return order


class ServiceOrderSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)
    service = ServiceSimpleSerializer(read_only=True)
    service_id = serializers.IntegerField(write_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = ServiceOrder
        fields = [
            'id', 'user', 'order_number', 'service', 'service_id', 'status', 'status_display',
            'service_price', 'addons_price', 'tax_amount', 'total_amount',
            'appointment_date', 'appointment_time', 'duration_minutes', 'special_requests',
            'payment_method', 'payment_status', 'created_at', 'updated_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class OrderTrackingSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = OrderTracking
        fields = [
            'id', 'status', 'status_display', 'description', 'location',
            'tracking_number', 'created_at'
        ]


class OrderWithTrackingSerializer(OrderSerializer):
    tracking = OrderTrackingSerializer(many=True, read_only=True)

    class Meta(OrderSerializer.Meta):
        fields = OrderSerializer.Meta.fields + ['tracking']


class OrderRefundSerializer(serializers.ModelSerializer):
    order = OrderSerializer(read_only=True)
    order_id = serializers.IntegerField(write_only=True)
    reason_display = serializers.CharField(source='get_reason_display', read_only=True)

    class Meta:
        model = OrderRefund
        fields = [
            'id', 'order', 'order_id', 'reason', 'reason_display',
            'description', 'refund_amount', 'is_approved', 'is_processed',
            'processed_at', 'created_at'
        ]


class CouponSerializer(serializers.ModelSerializer):
    discount_type_display = serializers.CharField(source='get_discount_type_display', read_only=True)
    is_valid = serializers.ReadOnlyField()

    class Meta:
        model = Coupon
        fields = [
            'id', 'code', 'discount_type', 'discount_type_display', 'discount_value',
            'minimum_order_amount', 'maximum_discount_amount', 'usage_limit',
            'used_count', 'is_active', 'is_valid', 'valid_from', 'valid_until'
        ]


class ApplyCouponSerializer(serializers.Serializer):
    coupon_code = serializers.CharField(max_length=50)
    order_amount = serializers.DecimalField(max_digits=10, decimal_places=2)

    def validate_coupon_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value.upper())
            if not coupon.is_valid:
                raise serializers.ValidationError("This coupon is not valid or has expired.")
            return value.upper()
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("Invalid coupon code.")


class OrderStatsSerializer(serializers.Serializer):
    total_orders = serializers.IntegerField()
    pending_orders = serializers.IntegerField()
    completed_orders = serializers.IntegerField()
    total_revenue = serializers.DecimalField(max_digits=15, decimal_places=2)
    average_order_value = serializers.DecimalField(max_digits=10, decimal_places=2)
