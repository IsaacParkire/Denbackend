from django.urls import path
from . import views

app_name = 'payments'

urlpatterns = [
    # Payments
    path('', views.PaymentListView.as_view(), name='payment-list'),
    path('<int:pk>/', views.PaymentDetailView.as_view(), name='payment-detail'),
    path('all/', views.AllPaymentsView.as_view(), name='all-payments'),
    
    # Payment Methods
    path('mpesa/', views.MpesaPaymentListView.as_view(), name='mpesa-payments'),
    path('cards/', views.CardPaymentListView.as_view(), name='card-payments'),
    
    # Payment Initiation
    path('initiate/mpesa/', views.initiate_mpesa_payment, name='initiate-mpesa'),
    path('initiate/card/', views.initiate_card_payment, name='initiate-card'),
    
    # Refunds
    path('refunds/', views.PaymentRefundListView.as_view(), name='refund-list'),
    path('<str:payment_id>/refund/', views.request_refund, name='request-refund'),
    
    # Statistics
    path('stats/', views.payment_stats, name='payment-stats'),
    path('dashboard-stats/', views.payment_dashboard_stats, name='dashboard-stats'),
    path('methods-stats/', views.payment_methods_stats, name='methods-stats'),
    
    # Webhooks
    path('webhooks/mpesa/', views.mpesa_webhook, name='mpesa-webhook'),
]
