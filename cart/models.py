from django.db import models
from django.contrib.auth import get_user_model
from products.models import Product, ProductVariant

User = get_user_model()


class Cart(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='cart')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart for {self.user.email}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def is_empty(self):
        return not self.items.exists()


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart', 'product', 'variant']

    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"{self.product.name}{variant_str} x{self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def save(self, *args, **kwargs):
        # Ensure quantity doesn't exceed available stock
        available_stock = self.variant.stock if self.variant else self.product.stock
        if self.quantity > available_stock:
            self.quantity = available_stock
        super().save(*args, **kwargs)


class SavedItem(models.Model):
    """Wishlist/Saved for later items"""
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='saved_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product', 'variant']

    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"Saved: {self.product.name}{variant_str}"


class CartSession(models.Model):
    """For anonymous users - session-based cart"""
    session_key = models.CharField(max_length=40, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Session Cart: {self.session_key}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartSessionItem(models.Model):
    cart_session = models.ForeignKey(CartSession, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    variant = models.ForeignKey(ProductVariant, on_delete=models.CASCADE, blank=True, null=True)
    quantity = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['cart_session', 'product', 'variant']

    def __str__(self):
        variant_str = f" ({self.variant.name})" if self.variant else ""
        return f"Session: {self.product.name}{variant_str} x{self.quantity}"

    @property
    def unit_price(self):
        if self.variant:
            return self.variant.price
        return self.product.price

    @property
    def subtotal(self):
        return self.unit_price * self.quantity
