from django.contrib import admin
from django.utils.html import format_html
from django.db import models
from django.forms import Textarea
from .models import (
    MainCategory, SubCategory, Category, Product, ProductImage, 
    ProductVariant, ProductReview, Wishlist
)

class SubCategoryInline(admin.TabularInline):
    model = SubCategory
    extra = 1
    fields = ('name', 'slug', 'icon', 'is_active', 'order')
    prepopulated_fields = {'slug': ('name',)}

class ProductImageInline(admin.TabularInline):
    model = ProductImage
    extra = 1
    fields = ('image', 'alt_text', 'is_primary', 'order')
    
    def get_extra(self, request, obj=None, **kwargs):
        return 3 if obj is None else 1

class ProductVariantInline(admin.TabularInline):
    model = ProductVariant
    extra = 1
    fields = ('name', 'value', 'price_adjustment', 'stock_quantity', 'sku_suffix')

@admin.register(MainCategory)
class MainCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'page', 'subcategory_count', 'product_count', 'is_active', 'order')
    list_filter = ('page', 'is_active')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    inlines = [SubCategoryInline]
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'page', 'icon', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        })
    )
    
    def subcategory_count(self, obj):
        return obj.subcategories.count()
    subcategory_count.short_description = 'Subcategories'
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'main_category', 'product_count', 'is_active', 'order')
    list_filter = ('main_category__page', 'main_category', 'is_active')
    search_fields = ('name', 'description', 'main_category__name')
    prepopulated_fields = {'slug': ('name',)}
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('main_category', 'name', 'slug', 'icon', 'description')
        }),
        ('Media', {
            'fields': ('image',)
        }),
        ('Display Settings', {
            'fields': ('is_active', 'order')
        })
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'main_category', 'sub_category', 'is_active', 'product_count', 'created_at')
    list_filter = ('is_active', 'main_category__page', 'main_category', 'created_at')
    search_fields = ('name', 'description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at',)
    
    fieldsets = (
        ('Legacy Category Information', {
            'fields': ('name', 'slug', 'description', 'image'),
            'description': 'This is a legacy category. Use Main Categories and Sub Categories instead.'
        }),
        ('Link to New System', {
            'fields': ('main_category', 'sub_category'),
            'description': 'Link this legacy category to the new category system'
        }),
        ('Settings', {
            'fields': ('is_active',)
        })
    )
    
    def product_count(self, obj):
        return obj.products.count()
    product_count.short_description = 'Products'

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = (
        'name', 'main_category', 'sub_category', 'price', 'stock_quantity', 
        'is_active', 'is_featured', 'is_exclusive', 'created_at'
    )
    list_filter = (
        'main_category__page', 'main_category', 'sub_category', 'is_active', 
        'is_featured', 'is_exclusive', 'is_limited_edition', 'is_bestseller', 
        'is_new_arrival', 'is_digital', 'created_at'
    )
    search_fields = ('name', 'sku', 'description', 'short_description')
    prepopulated_fields = {'slug': ('name',)}
    readonly_fields = ('created_at', 'updated_at')
    inlines = [ProductImageInline, ProductVariantInline]
    
    formfield_overrides = {
        models.TextField: {'widget': Textarea(attrs={'rows': 4, 'cols': 40})},
    }
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('name', 'slug', 'description', 'short_description')
        }),
        ('Categories', {
            'fields': ('main_category', 'sub_category', 'category'),
            'description': 'Select main category and subcategory. Legacy category is optional.'
        }),
        ('Pricing', {
            'fields': ('price', 'original_price', 'discount_percentage')
        }),
        ('Inventory', {
            'fields': ('sku', 'stock_quantity', 'low_stock_threshold')
        }),
        ('Product Details', {
            'fields': ('weight', 'dimensions', 'is_digital')
        }),
        ('Status & Flags', {
            'fields': (
                ('is_active', 'is_featured'),
                ('is_exclusive', 'is_limited_edition'),
                ('is_bestseller', 'is_new_arrival')
            )
        }),
        ('SEO', {
            'fields': ('meta_title', 'meta_description'),
            'classes': ('collapse',)
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        })
    )
    
    def get_form(self, request, obj=None, **kwargs):
        form = super().get_form(request, obj, **kwargs)
        
        # Filter subcategories based on selected main category
        if 'sub_category' in form.base_fields:
            if obj and obj.main_category:
                form.base_fields['sub_category'].queryset = SubCategory.objects.filter(
                    main_category=obj.main_category, is_active=True
                )
            else:
                form.base_fields['sub_category'].queryset = SubCategory.objects.none()
                
        return form

    class Media:
        js = ('admin/js/product_category_filter.js',)

@admin.register(ProductImage)
class ProductImageAdmin(admin.ModelAdmin):
    list_display = ('product', 'image_preview', 'is_primary', 'order', 'alt_text')
    list_filter = ('is_primary', 'product__main_category__page', 'product__main_category')
    search_fields = ('product__name', 'alt_text')
    list_editable = ('is_primary', 'order')
    
    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" width="50" height="50" style="object-fit: cover; border-radius: 4px;" />',
                obj.image.url
            )
        return "No Image"
    image_preview.short_description = 'Preview'

@admin.register(ProductReview)
class ProductReviewAdmin(admin.ModelAdmin):
    list_display = ('product', 'user', 'rating', 'is_verified_purchase', 'is_approved', 'created_at')
    list_filter = ('rating', 'is_verified_purchase', 'is_approved', 'product__main_category__page', 'created_at')
    search_fields = ('product__name', 'user__email', 'title', 'comment')
    readonly_fields = ('created_at',)

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ('user', 'product', 'created_at')
    list_filter = ('created_at', 'product__main_category__page', 'product__main_category')
    search_fields = ('user__email', 'product__name')