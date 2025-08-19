from rest_framework import serializers
from .models import Cart, CartItem, SavedItem, CartSession, CartSessionItem
from products.serializers import ProductSimpleSerializer, ProductVariantSerializer


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unit_price = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'unit_price', 'subtotal', 'created_at', 'updated_at'
        ]

    def validate(self, data):
        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)

        # Import here to avoid circular imports
        from products.models import Product, ProductVariant

        try:
            product = Product.objects.get(id=product_id)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found")

        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                if quantity > variant.stock:
                    raise serializers.ValidationError(
                        f"Only {variant.stock} items available for this variant"
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found")
        else:
            if quantity > product.stock:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available"
                )

        return data


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()
    is_empty = serializers.ReadOnlyField()

    class Meta:
        model = Cart
        fields = [
            'id', 'items', 'total_items', 'total_price', 'is_empty',
            'created_at', 'updated_at'
        ]


class AddToCartSerializer(serializers.Serializer):
    product_id = serializers.IntegerField()
    variant_id = serializers.IntegerField(required=False, allow_null=True)
    quantity = serializers.IntegerField(min_value=1, default=1)

    def validate(self, data):
        # Import here to avoid circular imports
        from products.models import Product, ProductVariant

        product_id = data.get('product_id')
        variant_id = data.get('variant_id')
        quantity = data.get('quantity', 1)

        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            raise serializers.ValidationError("Product not found or not available")

        if variant_id:
            try:
                variant = ProductVariant.objects.get(id=variant_id, product=product)
                if quantity > variant.stock:
                    raise serializers.ValidationError(
                        f"Only {variant.stock} items available for this variant"
                    )
            except ProductVariant.DoesNotExist:
                raise serializers.ValidationError("Product variant not found")
        else:
            if quantity > product.stock:
                raise serializers.ValidationError(
                    f"Only {product.stock} items available"
                )

        return data


class UpdateCartItemSerializer(serializers.Serializer):
    quantity = serializers.IntegerField(min_value=0)

    def validate_quantity(self, value):
        cart_item = self.instance
        if cart_item:
            available_stock = (cart_item.variant.stock if cart_item.variant 
                              else cart_item.product.stock)
            if value > available_stock:
                raise serializers.ValidationError(
                    f"Only {available_stock} items available"
                )
        return value


class SavedItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)

    class Meta:
        model = SavedItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id', 'created_at'
        ]

    def create(self, validated_data):
        validated_data['user'] = self.context['request'].user
        return super().create(validated_data)


class CartSessionItemSerializer(serializers.ModelSerializer):
    product = ProductSimpleSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)
    variant = ProductVariantSerializer(read_only=True)
    variant_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    unit_price = serializers.ReadOnlyField()
    subtotal = serializers.ReadOnlyField()

    class Meta:
        model = CartSessionItem
        fields = [
            'id', 'product', 'product_id', 'variant', 'variant_id',
            'quantity', 'unit_price', 'subtotal', 'created_at', 'updated_at'
        ]


class CartSessionSerializer(serializers.ModelSerializer):
    items = CartSessionItemSerializer(many=True, read_only=True)
    total_items = serializers.ReadOnlyField()
    total_price = serializers.ReadOnlyField()

    class Meta:
        model = CartSession
        fields = [
            'id', 'session_key', 'items', 'total_items', 'total_price',
            'created_at', 'updated_at'
        ]


class MoveToCartSerializer(serializers.Serializer):
    saved_item_id = serializers.IntegerField()
    quantity = serializers.IntegerField(min_value=1, default=1)
