from rest_framework import generics, filters, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django_filters.rest_framework import DjangoFilterBackend
from django.db.models import Q, Sum, Count, Avg
from django.shortcuts import get_object_or_404
from .models import (
    Payment, PaymentRefund, MpesaPayment, CardPayment,
    PaymentWebhook, PaymentAttempt, PaymentStatus, PaymentMethod
)
from .serializers import (
    PaymentSerializer, CreatePaymentSerializer, MpesaPaymentSerializer,
    InitiateMpesaPaymentSerializer, CardPaymentSerializer, InitiateCardPaymentSerializer,
    PaymentRefundSerializer, PaymentWebhookSerializer, PaymentAttemptSerializer,
    PaymentStatsSerializer, PaymentMethodStatsSerializer
)


class PaymentListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'currency']
    search_fields = ['payment_id', 'gateway_transaction_id', 'description']
    ordering_fields = ['created_at', 'amount', 'completed_at']
    ordering = ['-created_at']

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return CreatePaymentSerializer
        return PaymentSerializer


class PaymentDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = PaymentSerializer

    def get_queryset(self):
        return Payment.objects.filter(user=self.request.user)


class AllPaymentsView(generics.ListAPIView):
    """Admin view to see all payments"""
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['status', 'payment_method', 'currency', 'user']
    search_fields = [
        'payment_id', 'gateway_transaction_id', 'user__email',
        'user__first_name', 'user__last_name'
    ]
    ordering_fields = ['created_at', 'amount', 'completed_at']
    ordering = ['-created_at']


class PaymentRefundListView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticated]
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status']
    ordering = ['-created_at']

    def get_queryset(self):
        return PaymentRefund.objects.filter(payment__user=self.request.user)

    def get_serializer_class(self):
        return PaymentRefundSerializer


class MpesaPaymentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = MpesaPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['payment__status']
    search_fields = ['phone_number', 'mpesa_receipt_number']
    ordering = ['-payment__created_at']

    def get_queryset(self):
        return MpesaPayment.objects.filter(payment__user=self.request.user)


class CardPaymentListView(generics.ListAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = CardPaymentSerializer
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['payment__status', 'card_brand']
    ordering = ['-payment__created_at']

    def get_queryset(self):
        return CardPayment.objects.filter(payment__user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_mpesa_payment(request):
    """Initiate M-Pesa STK Push payment"""
    serializer = InitiateMpesaPaymentSerializer(data=request.data)
    if serializer.is_valid():
        phone_number = serializer.validated_data['phone_number']
        amount = serializer.validated_data['amount']
        order_id = serializer.validated_data.get('order_id')
        service_order_id = serializer.validated_data.get('service_order_id')
        description = serializer.validated_data.get('description', 'Payment for Laydies Den')

        # Create payment record
        payment_data = {
            'user': request.user,
            'amount': amount,
            'currency': 'KES',
            'payment_method': PaymentMethod.MPESA,
            'description': description,
            'status': PaymentStatus.PENDING
        }
        
        if order_id:
            from orders.models import Order
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                payment_data['order'] = order
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=400)
        
        if service_order_id:
            from orders.models import ServiceOrder
            try:
                service_order = ServiceOrder.objects.get(id=service_order_id, user=request.user)
                payment_data['service_order'] = service_order
            except ServiceOrder.DoesNotExist:
                return Response({'error': 'Service order not found'}, status=400)

        payment = Payment.objects.create(**payment_data)
        
        # Create M-Pesa specific record
        mpesa_payment = MpesaPayment.objects.create(
            payment=payment,
            phone_number=phone_number
        )

        # Here you would integrate with M-Pesa API
        # For now, we'll simulate the process
        try:
            # Simulate M-Pesa STK Push
            # In production, call actual M-Pesa API here
            mpesa_payment.merchant_request_id = f"MR{payment.payment_id[:8]}"
            mpesa_payment.checkout_request_id = f"CR{payment.payment_id[:8]}"
            mpesa_payment.save()
            
            payment.gateway_reference = mpesa_payment.checkout_request_id
            payment.save()

            return Response({
                'payment_id': payment.payment_id,
                'checkout_request_id': mpesa_payment.checkout_request_id,
                'message': 'STK Push sent to your phone. Please enter your M-Pesa PIN to complete payment.'
            }, status=201)

        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(e)
            payment.save()
            
            return Response({'error': 'Failed to initiate M-Pesa payment'}, status=400)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def initiate_card_payment(request):
    """Initiate card payment"""
    serializer = InitiateCardPaymentSerializer(data=request.data)
    if serializer.is_valid():
        # Extract card details
        card_number = serializer.validated_data['card_number']
        amount = serializer.validated_data['amount']
        order_id = serializer.validated_data.get('order_id')
        service_order_id = serializer.validated_data.get('service_order_id')

        # Create payment record
        payment_data = {
            'user': request.user,
            'amount': amount,
            'currency': 'KES',
            'payment_method': PaymentMethod.CARD,
            'description': 'Card payment for Laydies Den',
            'status': PaymentStatus.PROCESSING
        }
        
        if order_id:
            from orders.models import Order
            try:
                order = Order.objects.get(id=order_id, user=request.user)
                payment_data['order'] = order
            except Order.DoesNotExist:
                return Response({'error': 'Order not found'}, status=400)
        
        if service_order_id:
            from orders.models import ServiceOrder
            try:
                service_order = ServiceOrder.objects.get(id=service_order_id, user=request.user)
                payment_data['service_order'] = service_order
            except ServiceOrder.DoesNotExist:
                return Response({'error': 'Service order not found'}, status=400)

        payment = Payment.objects.create(**payment_data)
        
        # Create card payment record
        card_payment = CardPayment.objects.create(
            payment=payment,
            last_four=card_number[-4:],
            expiry_month=serializer.validated_data['expiry_month'],
            expiry_year=serializer.validated_data['expiry_year'],
            cardholder_name=serializer.validated_data['cardholder_name']
        )

        # Here you would integrate with payment gateway (Stripe, PayPal, etc.)
        # For simulation purposes
        try:
            # Simulate payment processing
            import random
            if random.choice([True, False, True]):  # 66% success rate
                payment.status = PaymentStatus.COMPLETED
                payment.gateway_transaction_id = f"TXN{payment.payment_id[:8]}"
                payment.save()
                
                return Response({
                    'payment_id': payment.payment_id,
                    'status': 'completed',
                    'message': 'Payment successful'
                }, status=200)
            else:
                payment.status = PaymentStatus.FAILED
                payment.failure_reason = 'Card declined'
                payment.save()
                
                return Response({'error': 'Payment failed. Card declined.'}, status=400)

        except Exception as e:
            payment.status = PaymentStatus.FAILED
            payment.failure_reason = str(e)
            payment.save()
            
            return Response({'error': 'Payment processing failed'}, status=400)

    return Response(serializer.errors, status=400)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def request_refund(request, payment_id):
    """Request a refund for a payment"""
    try:
        payment = Payment.objects.get(payment_id=payment_id, user=request.user)
    except Payment.DoesNotExist:
        return Response({'error': 'Payment not found'}, status=404)

    if not payment.can_be_refunded:
        return Response({'error': 'Payment cannot be refunded'}, status=400)

    reason = request.data.get('reason', 'Customer requested refund')
    amount = request.data.get('amount', payment.amount)

    # Validate refund amount
    if amount > payment.amount:
        return Response({'error': 'Refund amount cannot exceed payment amount'}, status=400)

    # Check if total refunds would exceed payment amount
    existing_refunds = PaymentRefund.objects.filter(
        payment=payment, 
        status__in=[PaymentStatus.COMPLETED, PaymentStatus.PROCESSING]
    ).aggregate(total=Sum('amount'))['total'] or 0

    if existing_refunds + amount > payment.amount:
        return Response({'error': 'Total refund amount would exceed payment amount'}, status=400)

    # Create refund record
    refund = PaymentRefund.objects.create(
        payment=payment,
        amount=amount,
        reason=reason,
        status=PaymentStatus.PENDING
    )

    return Response({
        'refund_id': refund.refund_id,
        'amount': refund.amount,
        'status': refund.status,
        'message': 'Refund request submitted successfully'
    }, status=201)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def payment_stats(request):
    """Get payment statistics for current user"""
    user_payments = Payment.objects.filter(user=request.user)
    
    stats = {
        'total_payments': user_payments.count(),
        'successful_payments': user_payments.filter(status=PaymentStatus.COMPLETED).count(),
        'failed_payments': user_payments.filter(status=PaymentStatus.FAILED).count(),
        'total_amount': user_payments.filter(status=PaymentStatus.COMPLETED).aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'total_refunds': PaymentRefund.objects.filter(
            payment__user=request.user, status=PaymentStatus.COMPLETED
        ).count(),
        'refund_amount': PaymentRefund.objects.filter(
            payment__user=request.user, status=PaymentStatus.COMPLETED
        ).aggregate(total=Sum('amount'))['total'] or 0
    }
    
    return Response(stats)


@api_view(['GET'])
def payment_dashboard_stats(request):
    """Get overall payment statistics (admin view)"""
    all_payments = Payment.objects.all()
    
    stats = {
        'total_payments': all_payments.count(),
        'successful_payments': all_payments.filter(status=PaymentStatus.COMPLETED).count(),
        'failed_payments': all_payments.filter(status=PaymentStatus.FAILED).count(),
        'pending_payments': all_payments.filter(status=PaymentStatus.PENDING).count(),
        'total_revenue': all_payments.filter(status=PaymentStatus.COMPLETED).aggregate(
            total=Sum('amount')
        )['total'] or 0,
        'average_payment': all_payments.filter(status=PaymentStatus.COMPLETED).aggregate(
            avg=Avg('amount')
        )['avg'] or 0,
        'refund_count': PaymentRefund.objects.filter(status=PaymentStatus.COMPLETED).count(),
        'total_refunded': PaymentRefund.objects.filter(status=PaymentStatus.COMPLETED).aggregate(
            total=Sum('amount')
        )['total'] or 0
    }
    
    return Response(stats)


@api_view(['GET'])
def payment_methods_stats(request):
    """Get statistics by payment method"""
    from django.db.models import F, Case, When, IntegerField
    
    method_stats = []
    
    for method, method_name in PaymentMethod.choices:
        payments = Payment.objects.filter(payment_method=method)
        successful_payments = payments.filter(status=PaymentStatus.COMPLETED)
        
        total_count = payments.count()
        success_count = successful_payments.count()
        success_rate = (success_count / total_count * 100) if total_count > 0 else 0
        
        method_stats.append({
            'payment_method': method_name,
            'count': total_count,
            'total_amount': successful_payments.aggregate(total=Sum('amount'))['total'] or 0,
            'success_rate': round(success_rate, 2)
        })
    
    return Response(method_stats)


@api_view(['POST'])
def mpesa_webhook(request):
    """Handle M-Pesa webhook notifications"""
    # This endpoint would handle M-Pesa callback
    # For security, you should validate the request
    
    data = request.data
    
    # Create webhook record
    webhook = PaymentWebhook.objects.create(
        payment_method=PaymentMethod.MPESA,
        event_type=data.get('event_type', 'payment_notification'),
        data=data
    )
    
    # Process the webhook data
    try:
        # Extract relevant information from M-Pesa callback
        checkout_request_id = data.get('CheckoutRequestID')
        result_code = data.get('ResultCode')
        
        if checkout_request_id:
            try:
                mpesa_payment = MpesaPayment.objects.get(checkout_request_id=checkout_request_id)
                payment = mpesa_payment.payment
                
                if result_code == 0:  # Success
                    payment.status = PaymentStatus.COMPLETED
                    payment.gateway_transaction_id = data.get('MpesaReceiptNumber')
                    mpesa_payment.mpesa_receipt_number = data.get('MpesaReceiptNumber')
                    
                    from django.utils import timezone
                    payment.completed_at = timezone.now()
                else:
                    payment.status = PaymentStatus.FAILED
                    payment.failure_reason = data.get('ResultDesc', 'Payment failed')
                
                payment.gateway_response = data
                payment.save()
                mpesa_payment.save()
                
                webhook.processed = True
                webhook.save()
                
            except MpesaPayment.DoesNotExist:
                pass  # Payment not found, might be a different transaction
        
        return Response({'status': 'success'}, status=200)
        
    except Exception as e:
        return Response({'status': 'error', 'message': str(e)}, status=400)
