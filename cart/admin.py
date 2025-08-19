from django.contrib import admin
from .models import Cart, CartItem, SavedItem, CartSession, CartSessionItem


class CartItemInline(admin.TabularInline):
    model = CartItem
    extra = 0
    readonly_fields = ['unit_price', 'subtotal']


@admin.register(Cart)
class CartAdmin(admin.ModelAdmin):
    list_display = ['user', 'total_items', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['user__email', 'user__first_name', 'user__last_name']
    readonly_fields = ['total_items', 'total_price', 'is_empty', 'created_at', 'updated_at']
    inlines = [CartItemInline]
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related('user')


@admin.register(CartItem)
class CartItemAdmin(admin.ModelAdmin):
    list_display = ['cart', 'product', 'variant', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['created_at', 'product__category']
    search_fields = [
        'cart__user__email', 'product__name', 'variant__name'
    ]
    readonly_fields = ['unit_price', 'subtotal', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cart__user', 'product', 'variant'
        )


@admin.register(SavedItem)
class SavedItemAdmin(admin.ModelAdmin):
    list_display = ['user', 'product', 'variant', 'created_at']
    list_filter = ['created_at', 'product__category']
    search_fields = [
        'user__email', 'user__first_name', 'user__last_name',
        'product__name', 'variant__name'
    ]
    readonly_fields = ['created_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'user', 'product', 'variant'
        )


class CartSessionItemInline(admin.TabularInline):
    model = CartSessionItem
    extra = 0
    readonly_fields = ['unit_price', 'subtotal']


@admin.register(CartSession)
class CartSessionAdmin(admin.ModelAdmin):
    list_display = ['session_key', 'total_items', 'total_price', 'created_at', 'updated_at']
    list_filter = ['created_at', 'updated_at']
    search_fields = ['session_key']
    readonly_fields = ['total_items', 'total_price', 'created_at', 'updated_at']
    inlines = [CartSessionItemInline]


@admin.register(CartSessionItem)
class CartSessionItemAdmin(admin.ModelAdmin):
    list_display = ['cart_session', 'product', 'variant', 'quantity', 'unit_price', 'subtotal']
    list_filter = ['created_at', 'product__category']
    search_fields = ['cart_session__session_key', 'product__name', 'variant__name']
    readonly_fields = ['unit_price', 'subtotal', 'created_at', 'updated_at']
    
    def get_queryset(self, request):
        return super().get_queryset(request).select_related(
            'cart_session', 'product', 'variant'
        )
