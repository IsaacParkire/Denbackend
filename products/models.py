from django.db import models
from pyuploadcare.dj.models import ImageField
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator

User = get_user_model()

# Main Categories (Page-level categories)
class MainCategory(models.Model):
    PAGE_CHOICES = [
        ('boutique', 'Her Boutique'),
        ('toys', 'Her Toys'),
        ('scent', 'Her Scent'),
    ]
    
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    page = models.CharField(max_length=20, choices=PAGE_CHOICES)
    description = models.TextField(blank=True)
    image = ImageField(blank=True, manual_crop='', null=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon for the category")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Main Categories"
        ordering = ['page', 'order', 'name']
        unique_together = ['name', 'page']
    
    def __str__(self):
        return f"{self.get_page_display()} - {self.name}"

# Subcategories within each main category
class SubCategory(models.Model):
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='subcategories')
    name = models.CharField(max_length=100)
    slug = models.SlugField()
    description = models.TextField(blank=True)
    image = ImageField(blank=True, manual_crop='', null=True)
    icon = models.CharField(max_length=10, blank=True, help_text="Emoji icon for the subcategory")
    is_active = models.BooleanField(default=True)
    order = models.PositiveIntegerField(default=0, help_text="Display order within main category")
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Sub Categories"
        ordering = ['main_category', 'order', 'name']
        unique_together = ['main_category', 'slug']
    
    def __str__(self):
        return f"{self.main_category.name} - {self.name}"

# Legacy Category model for backward compatibility
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    description = models.TextField(blank=True)
    image = ImageField(blank=True, manual_crop='', null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    # Link to new category system
    main_category = models.ForeignKey(MainCategory, on_delete=models.SET_NULL, null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.SET_NULL, null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Categories (Legacy)"
        ordering = ['name']
    
    def __str__(self):
        return self.name

class Product(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    
    # New category system - allow null temporarily for migration
    main_category = models.ForeignKey(MainCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    sub_category = models.ForeignKey(SubCategory, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Legacy category for backward compatibility
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='products', null=True, blank=True)
    
    # Pricing
    price = models.DecimalField(max_digits=10, decimal_places=2)
    original_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    discount_percentage = models.PositiveIntegerField(default=0, validators=[MaxValueValidator(100)])
    
    # Inventory
    stock_quantity = models.PositiveIntegerField(default=0)
    low_stock_threshold = models.PositiveIntegerField(default=5)
    
    # Product Details
    sku = models.CharField(max_length=100, unique=True)
    weight = models.DecimalField(max_digits=5, decimal_places=2, blank=True, null=True, help_text="Weight in kg")
    dimensions = models.CharField(max_length=100, blank=True, help_text="L x W x H in cm")
    
    # Product Status
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    is_digital = models.BooleanField(default=False)
    
    # Product flags
    is_exclusive = models.BooleanField(default=False, help_text="Exclusive product")
    is_limited_edition = models.BooleanField(default=False, help_text="Limited edition product")
    is_bestseller = models.BooleanField(default=False, help_text="Bestseller product")
    is_new_arrival = models.BooleanField(default=False, help_text="New arrival product")
    
    # SEO
    meta_title = models.CharField(max_length=60, blank=True)
    meta_description = models.CharField(max_length=160, blank=True)

    # Uploadcare image field
    from pyuploadcare.dj.models import ImageField
    image = ImageField(blank=True, manual_crop='')
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return self.name
    
    @property
    def is_on_sale(self):
        return self.original_price and self.original_price > self.price
    
    @property
    def is_in_stock(self):
        return self.stock_quantity > 0
    
    @property
    def is_low_stock(self):
        return self.stock_quantity <= self.low_stock_threshold
    
    def delete(self, *args, **kwargs):
        # Delete the main product image from Uploadcare before deleting the product
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='images')
    image = ImageField(blank=True, manual_crop='')
    alt_text = models.CharField(max_length=200, blank=True)
    is_primary = models.BooleanField(default=False)
    order = models.PositiveIntegerField(default=0)
    
    class Meta:
        ordering = ['order']
    
    def __str__(self):
        return f"{self.product.name} - Image {self.order}"
    
    def delete(self, *args, **kwargs):
        # Delete the image from Uploadcare before deleting the model instance
        if self.image:
            self.image.delete()
        super().delete(*args, **kwargs)

class ProductVariant(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='variants')
    name = models.CharField(max_length=100)  # e.g., "Size", "Color"
    value = models.CharField(max_length=100)  # e.g., "Medium", "Red"
    price_adjustment = models.DecimalField(max_digits=8, decimal_places=2, default=0)
    stock_quantity = models.PositiveIntegerField(default=0)
    sku_suffix = models.CharField(max_length=50, blank=True)
    
    class Meta:
        unique_together = ['product', 'name', 'value']
    
    def __str__(self):
        return f"{self.product.name} - {self.name}: {self.value}"

class ProductReview(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.PositiveIntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['product', 'user']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.product.name} - {self.rating} stars by {self.user.email}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['user', 'product']
    
    def __str__(self):
        return f"{self.user.email} - {self.product.name}"