from django.urls import path
from . import views

app_name = 'orders'

urlpatterns = [
    # Orders
    path('', views.OrderListView.as_view(), name='order-list'),
    path('<int:pk>/', views.OrderDetailView.as_view(), name='order-detail'),
    path('all/', views.AllOrdersView.as_view(), name='all-orders'),
    
    # Order Actions
    path('<int:order_id>/cancel/', views.cancel_order, name='cancel-order'),
    path('from-cart/', views.create_order_from_cart, name='create-from-cart'),
    path('track/<str:order_number>/', views.track_order, name='track-order'),
    
    # Service Orders
    path('services/', views.ServiceOrderListView.as_view(), name='service-order-list'),
    path('services/<int:pk>/', views.ServiceOrderDetailView.as_view(), name='service-order-detail'),
    
    # Order Tracking
    path('tracking/', views.OrderTrackingListView.as_view(), name='tracking-list'),
    
    # Refunds
    path('refunds/', views.OrderRefundListView.as_view(), name='refund-list'),
    
    # Coupons
    path('coupons/', views.CouponListView.as_view(), name='coupon-list'),
    path('apply-coupon/', views.apply_coupon, name='apply-coupon'),
    
    # Statistics
    path('stats/', views.user_order_stats, name='user-stats'),
    path('dashboard-stats/', views.order_dashboard_stats, name='dashboard-stats'),
]
