from django.shortcuts import render
from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Avg, Count
from django.shortcuts import get_object_or_404
from .models import (
    Order, OrderItem, ServiceOrder, OrderTracking, 
    OrderRefund, Coupon, OrderStatus
)
from .serializers import (
    OrderSerializer, CreateOrderSerializer, ServiceOrderSerializer,
    OrderTrackingSerializer, OrderWithTrackingSerializer, OrderRefundSerializer,
    CouponSerializer, ApplyCouponSerializer, OrderStatsSerializer
)


class OrderListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'created_at']
    search_fields = ['order_number', 'shipping_email', 'billing_email']
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreateOrderSerializer
        return OrderSerializer


class OrderDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = OrderWithTrackingSerializer

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class AllOrdersView(generics.ListAPIView):
    """Admin view to see all orders"""
    queryset = Order.objects.all()
    serializer_class = OrderSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_status', 'created_at', 'user']
    search_fields = [
        'order_number', 'user__email', 'user__first_name', 'user__last_name',
        'shipping_email', 'billing_email'
    ]
    ordering_fields = ['created_at', 'updated_at', 'total_amount']
    ordering = ['-created_at']


class ServiceOrderListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'service', 'appointment_date']
    search_fields = ['order_number', 'service__name']
    ordering_fields = ['created_at', 'appointment_date']
    ordering = ['-created_at']

    def get_queryset(self):
        return ServiceOrder.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        return ServiceOrderSerializer


class ServiceOrderDetailView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceOrderSerializer

    def get_queryset(self):
        return ServiceOrder.objects.filter(user=self.request.user)


class OrderTrackingListView(generics.ListCreateAPIView):
    serializer_class = OrderTrackingSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['order', 'status']
    ordering = ['-created_at']

    def get_queryset(self):
        return OrderTracking.objects.all()


class OrderRefundListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['reason', 'is_approved', 'is_processed']
    ordering = ['-created_at']

    def get_queryset(self):
        return OrderRefund.objects.filter(order__user=self.request.user)

    def get_serializer_class(self):
        return OrderRefundSerializer


class CouponListView(generics.ListAPIView):
    queryset = Coupon.objects.filter(is_active=True)
    serializer_class = CouponSerializer
    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['code']
    ordering = ['valid_until']


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    """Cancel an order"""
    try:
        order = Order.objects.get(id=order_id, user=request.user)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    
    if order.status not in [OrderStatus.PENDING, OrderStatus.CONFIRMED]:
        return Response(
            {'error': 'Order cannot be cancelled (already processing or shipped)'},
            status=400
        )
    
    order.status = OrderStatus.CANCELLED
    order.save()
    
    # Create tracking entry
    OrderTracking.objects.create(
        order=order,
        status=OrderStatus.CANCELLED,
        description='Order cancelled by customer'
    )
    
    serializer = OrderSerializer(order)
    return Response(serializer.data)


@api_view(['POST'])
def apply_coupon(request):
    """Apply a coupon to calculate discount"""
    serializer = ApplyCouponSerializer(data=request.data)
    if serializer.is_valid():
        coupon_code = serializer.validated_data['coupon_code']
        order_amount = serializer.validated_data['order_amount']
        
        try:
            coupon = Coupon.objects.get(code=coupon_code)
            discount_amount = coupon.calculate_discount(order_amount)
            
            return Response({
                'coupon_code': coupon_code,
                'discount_amount': discount_amount,
                'new_total': order_amount - discount_amount
            })
        except Coupon.DoesNotExist:
            return Response({'error': 'Invalid coupon code'}, status=400)
    
    return Response(serializer.errors, status=400)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_order_stats(request):
    """Get order statistics for the current user"""
    user_orders = Order.objects.filter(user=request.user)
    
    stats = {
        'total_orders': user_orders.count(),
        'pending_orders': user_orders.filter(status=OrderStatus.PENDING).count(),
        'completed_orders': user_orders.filter(status=OrderStatus.DELIVERED).count(),
        'total_spent': user_orders.filter(
            status=OrderStatus.DELIVERED
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'average_order_value': user_orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
    }
    
    return Response(stats)


@api_view(['GET'])
def order_dashboard_stats(request):
    """Get overall order statistics (admin view)"""
    all_orders = Order.objects.all()
    
    stats = {
        'total_orders': all_orders.count(),
        'pending_orders': all_orders.filter(status=OrderStatus.PENDING).count(),
        'processing_orders': all_orders.filter(status=OrderStatus.PROCESSING).count(),
        'shipped_orders': all_orders.filter(status=OrderStatus.SHIPPED).count(),
        'delivered_orders': all_orders.filter(status=OrderStatus.DELIVERED).count(),
        'cancelled_orders': all_orders.filter(status=OrderStatus.CANCELLED).count(),
        'total_revenue': all_orders.filter(
            status=OrderStatus.DELIVERED
        ).aggregate(total=Sum('total_amount'))['total'] or 0,
        'average_order_value': all_orders.aggregate(
            avg=Avg('total_amount')
        )['avg'] or 0
    }
    
    return Response(stats)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_order_from_cart(request):
    """Create an order from the user's cart"""
    from cart.models import Cart
    
    try:
        cart = Cart.objects.get(user=request.user)
    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=400)
    
    if cart.is_empty:
        return Response({'error': 'Cart is empty'}, status=400)
    
    # Get shipping and billing information from request
    shipping_data = request.data.get('shipping', {})
    billing_data = request.data.get('billing', shipping_data)  # Use shipping if billing not provided
    
    # Create order
    order_data = {
        **shipping_data,
        'billing_first_name': billing_data.get('first_name', shipping_data.get('first_name')),
        'billing_last_name': billing_data.get('last_name', shipping_data.get('last_name')),
        'billing_email': billing_data.get('email', shipping_data.get('email')),
        'billing_phone': billing_data.get('phone', shipping_data.get('phone')),
        'billing_address_line_1': billing_data.get('address_line_1', shipping_data.get('address_line_1')),
        'billing_address_line_2': billing_data.get('address_line_2', shipping_data.get('address_line_2', '')),
        'billing_city': billing_data.get('city', shipping_data.get('city')),
        'billing_state': billing_data.get('state', shipping_data.get('state')),
        'billing_postal_code': billing_data.get('postal_code', shipping_data.get('postal_code')),
        'billing_country': billing_data.get('country', shipping_data.get('country', 'Kenya')),
        'notes': request.data.get('notes', ''),
        'payment_method': request.data.get('payment_method', ''),
        'subtotal': cart.total_price,
        'total_amount': cart.total_price,
        'user': request.user
    }
    
    order = Order.objects.create(**order_data)
    
    # Create order items from cart items
    for cart_item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            product=cart_item.product,
            variant=cart_item.variant,
            quantity=cart_item.quantity,
            unit_price=cart_item.unit_price,
            total_price=cart_item.subtotal
        )
    
    # Clear the cart
    cart.items.all().delete()
    
    # Create initial tracking entry
    OrderTracking.objects.create(
        order=order,
        status=OrderStatus.PENDING,
        description='Order created successfully'
    )
    
    serializer = OrderWithTrackingSerializer(order)
    return Response(serializer.data, status=status.HTTP_201_CREATED)


@api_view(['GET'])
def track_order(request, order_number):
    """Track an order by order number (public endpoint)"""
    try:
        order = Order.objects.get(order_number=order_number)
    except Order.DoesNotExist:
        return Response({'error': 'Order not found'}, status=404)
    
    serializer = OrderWithTrackingSerializer(order)
    return Response(serializer.data)
