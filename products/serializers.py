from rest_framework import serializers
from .models import (
    MainCategory, SubCategory, Category, Product, ProductImage, 
    ProductVariant, ProductReview, Wishlist
)

# ------------------------------
# CATEGORY SERIALIZERS
# ------------------------------
class MainCategorySerializer(serializers.ModelSerializer):
    subcategory_count = serializers.SerializerMethodField()
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = MainCategory
        fields = [
            'id', 'name', 'slug', 'page', 'description',
            'image', 'icon', 'order', 'subcategory_count', 'product_count'
        ]
    
    def get_subcategory_count(self, obj):
        return obj.subcategories.filter(is_active=True).count()
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class SubCategorySerializer(serializers.ModelSerializer):
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = SubCategory
        fields = [
            'id', 'name', 'slug', 'main_category', 'main_category_name',
            'description', 'image', 'icon', 'order', 'product_count'
        ]
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


class CategorySerializer(serializers.ModelSerializer):
    product_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ['id', 'name', 'slug', 'description', 'image', 'product_count']
    
    def get_product_count(self, obj):
        return obj.products.filter(is_active=True).count()


# ------------------------------
# PRODUCT IMAGE SERIALIZER
# ------------------------------
class ProductImageSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = ProductImage
        fields = ['id', 'image', 'alt_text', 'is_primary', 'order']

    def get_image(self, obj):
        request = self.context.get('request')
        image_field = obj.image

        if not image_field:
            return None

        # Works for both Uploadcare (cdn_url) and regular Django ImageField (url)
        image_url = getattr(image_field, 'cdn_url', None) or getattr(image_field, 'url', None) or str(image_field)

        if request and image_url:
            return request.build_absolute_uri(image_url)
        return image_url


# ------------------------------
# PRODUCT VARIANT SERIALIZER
# ------------------------------
class ProductVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductVariant
        fields = ['id', 'name', 'value', 'price_adjustment', 'stock_quantity', 'sku_suffix']


# ------------------------------
# PRODUCT REVIEW SERIALIZER
# ------------------------------
class ProductReviewSerializer(serializers.ModelSerializer):
    user_name = serializers.CharField(source='user.get_full_name', read_only=True)
    
    class Meta:
        model = ProductReview
        fields = ['id', 'user', 'user_name', 'rating', 'title', 'comment', 'is_verified_purchase', 'created_at']
        read_only_fields = ['user', 'is_verified_purchase', 'created_at']


# ------------------------------
# PRODUCT LIST SERIALIZER
# ------------------------------
class ProductListSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    main_category_name = serializers.CharField(source='main_category.name', read_only=True)
    sub_category_name = serializers.CharField(source='sub_category.name', read_only=True)
    page = serializers.CharField(source='main_category.page', read_only=True)
    primary_image = serializers.SerializerMethodField()
    images = ProductImageSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'short_description', 'category_name', 
            'main_category_name', 'sub_category_name', 'page',
            'price', 'original_price', 'discount_percentage',
            'primary_image', 'images',
            'is_featured', 'is_exclusive', 'is_limited_edition',
            'is_bestseller', 'is_new_arrival', 'is_in_stock',
            'is_on_sale', 'average_rating', 'review_count'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            return None

        image_field = primary_image.image
        image_url = getattr(image_field, 'cdn_url', None) or getattr(image_field, 'url', None) or str(image_field)

        request = self.context.get('request')
        if request and image_url:
            return request.build_absolute_uri(image_url)
        return image_url

    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0

    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


# ------------------------------
# PRODUCT DETAIL SERIALIZER
# ------------------------------
class ProductDetailSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)
    main_category = MainCategorySerializer(read_only=True)
    sub_category = SubCategorySerializer(read_only=True)
    images = ProductImageSerializer(many=True, read_only=True)
    variants = ProductVariantSerializer(many=True, read_only=True)
    reviews = ProductReviewSerializer(many=True, read_only=True)
    average_rating = serializers.SerializerMethodField()
    review_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'description', 'short_description',
            'category', 'main_category', 'sub_category',
            'price', 'original_price', 'discount_percentage', 'stock_quantity',
            'sku', 'weight', 'dimensions', 'is_featured', 'is_digital',
            'is_exclusive', 'is_limited_edition', 'is_bestseller', 'is_new_arrival',
            'is_in_stock', 'is_on_sale', 'is_low_stock',
            'meta_title', 'meta_description', 'images', 'variants',
            'reviews', 'average_rating', 'review_count', 'created_at', 'updated_at'
        ]
    
    def get_average_rating(self, obj):
        reviews = obj.reviews.filter(is_approved=True)
        if reviews.exists():
            return round(sum(review.rating for review in reviews) / reviews.count(), 1)
        return 0
    
    def get_review_count(self, obj):
        return obj.reviews.filter(is_approved=True).count()


# ------------------------------
# WISHLIST SERIALIZER
# ------------------------------
class WishlistSerializer(serializers.ModelSerializer):
    product = ProductListSerializer(read_only=True)
    
    class Meta:
        model = Wishlist
        fields = ['id', 'product', 'created_at']
        read_only_fields = ['created_at']


# ------------------------------
# SIMPLE PRODUCT SERIALIZER
# ------------------------------
class ProductSimpleSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    primary_image = serializers.SerializerMethodField()
    
    class Meta:
        model = Product
        fields = [
            'id', 'name', 'slug', 'category_name',
            'price', 'primary_image', 'is_in_stock'
        ]
    
    def get_primary_image(self, obj):
        primary_image = obj.images.filter(is_primary=True).first()
        if not primary_image:
            return None

        image_field = primary_image.image
        image_url = getattr(image_field, 'cdn_url', None) or getattr(image_field, 'url', None) or str(image_field)

        request = self.context.get('request')
        if request and image_url:
            return request.build_absolute_uri(image_url)
        return image_url
