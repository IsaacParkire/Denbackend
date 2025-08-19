from django.urls import path
from . import views

app_name = 'cart'

urlpatterns = [
    # Cart
    path('', views.CartView.as_view(), name='cart-detail'),
    path('items/', views.CartItemListView.as_view(), name='cart-items'),
    path('items/<int:pk>/', views.CartItemDetailView.as_view(), name='cart-item-detail'),
    
    # Cart Actions
    path('add/', views.add_to_cart, name='add-to-cart'),
    path('remove/<int:item_id>/', views.remove_from_cart, name='remove-from-cart'),
    path('clear/', views.clear_cart, name='clear-cart'),
    path('update/<int:item_id>/', views.update_cart_item, name='update-cart-item'),
    
    # Saved Items (Wishlist)
    path('saved/', views.SavedItemListView.as_view(), name='saved-items'),
    path('saved/<int:pk>/', views.SavedItemDetailView.as_view(), name='saved-item-detail'),
    path('save-for-later/<int:item_id>/', views.save_for_later, name='save-for-later'),
    path('move-to-cart/', views.move_to_cart, name='move-to-cart'),
    
    # Session Cart (Anonymous Users)
    path('session/', views.session_cart, name='session-cart'),
    path('session/add/', views.add_to_session_cart, name='add-to-session-cart'),
    path('merge-session/', views.merge_session_cart, name='merge-session-cart'),
]
