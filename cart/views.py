from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from django.shortcuts import get_object_or_404
from .models import Cart, CartItem, SavedItem, CartSession, CartSessionItem
from .serializers import (
    CartSerializer, CartItemSerializer, AddToCartSerializer,
    UpdateCartItemSerializer, SavedItemSerializer, MoveToCartSerializer,
    CartSessionSerializer
)
from products.models import Product, ProductVariant


class CartView(generics.RetrieveAPIView):
    serializer_class = CartSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart


class CartItemListView(generics.ListAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()


class CartItemDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = CartItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        cart, created = Cart.objects.get_or_create(user=self.request.user)
        return cart.items.all()

    def get_serializer_class(self):
        if self.request.method in ['PUT', 'PATCH']:
            return UpdateCartItemSerializer
        return CartItemSerializer

    def perform_update(self, serializer):
        quantity = serializer.validated_data.get('quantity')
        cart_item = self.get_object()
        
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()

    def delete(self, request, *args, **kwargs):
        cart_item = self.get_object()
        cart_item.delete()
        return Response({'message': 'Item removed from cart'}, status=status.HTTP_204_NO_CONTENT)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def add_to_cart(request):
    """Add item to cart"""
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']

        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Check if item already exists in cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product_id=product_id,
            variant_id=variant_id,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            # Update quantity if item already exists
            cart_item.quantity += quantity
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, item_id):
    """Remove item from cart"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    cart_item.delete()
    
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def clear_cart(request):
    """Clear all items from cart"""
    cart, created = Cart.objects.get_or_create(user=request.user)
    cart.items.all().delete()
    
    cart_serializer = CartSerializer(cart)
    return Response(cart_serializer.data, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_cart_item(request, item_id):
    """Update cart item quantity"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    serializer = UpdateCartItemSerializer(cart_item, data=request.data)
    if serializer.is_valid():
        quantity = serializer.validated_data['quantity']
        
        if quantity == 0:
            cart_item.delete()
        else:
            cart_item.quantity = quantity
            cart_item.save()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class SavedItemListView(generics.ListCreateAPIView):
    serializer_class = SavedItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedItem.objects.filter(user=self.request.user)


class SavedItemDetailView(generics.RetrieveDestroyAPIView):
    serializer_class = SavedItemSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return SavedItem.objects.filter(user=self.request.user)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_for_later(request, item_id):
    """Move cart item to saved items"""
    cart = get_object_or_404(Cart, user=request.user)
    cart_item = get_object_or_404(CartItem, id=item_id, cart=cart)
    
    # Create saved item
    saved_item, created = SavedItem.objects.get_or_create(
        user=request.user,
        product=cart_item.product,
        variant=cart_item.variant
    )
    
    # Remove from cart
    cart_item.delete()
    
    return Response({'message': 'Item saved for later'}, status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def move_to_cart(request):
    """Move saved item to cart"""
    serializer = MoveToCartSerializer(data=request.data)
    if serializer.is_valid():
        saved_item_id = serializer.validated_data['saved_item_id']
        quantity = serializer.validated_data['quantity']
        
        saved_item = get_object_or_404(
            SavedItem, id=saved_item_id, user=request.user
        )
        
        cart, created = Cart.objects.get_or_create(user=request.user)
        
        # Add to cart
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=cart,
            product=saved_item.product,
            variant=saved_item.variant,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
        
        # Remove from saved items
        saved_item.delete()
        
        cart_serializer = CartSerializer(cart)
        return Response(cart_serializer.data, status=status.HTTP_200_OK)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


# Session-based cart for anonymous users
@api_view(['GET'])
def session_cart(request):
    """Get session cart for anonymous users"""
    if not request.session.session_key:
        request.session.create()
    
    session_key = request.session.session_key
    cart_session, created = CartSession.objects.get_or_create(session_key=session_key)
    
    serializer = CartSessionSerializer(cart_session)
    return Response(serializer.data)


@api_view(['POST'])
def add_to_session_cart(request):
    """Add item to session cart for anonymous users"""
    serializer = AddToCartSerializer(data=request.data)
    if serializer.is_valid():
        if not request.session.session_key:
            request.session.create()
        
        session_key = request.session.session_key
        cart_session, created = CartSession.objects.get_or_create(session_key=session_key)
        
        product_id = serializer.validated_data['product_id']
        variant_id = serializer.validated_data.get('variant_id')
        quantity = serializer.validated_data['quantity']
        
        # Check if item already exists
        cart_item, item_created = CartSessionItem.objects.get_or_create(
            cart_session=cart_session,
            product_id=product_id,
            variant_id=variant_id,
            defaults={'quantity': quantity}
        )
        
        if not item_created:
            cart_item.quantity += quantity
            cart_item.save()
        
        cart_serializer = CartSessionSerializer(cart_session)
        return Response(cart_serializer.data, status=status.HTTP_201_CREATED)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def merge_session_cart(request):
    """Merge session cart with user cart on login"""
    if not request.session.session_key:
        return Response({'message': 'No session cart found'}, status=status.HTTP_200_OK)
    
    session_key = request.session.session_key
    
    try:
        cart_session = CartSession.objects.get(session_key=session_key)
    except CartSession.DoesNotExist:
        return Response({'message': 'No session cart found'}, status=status.HTTP_200_OK)
    
    user_cart, created = Cart.objects.get_or_create(user=request.user)
    
    # Merge session cart items with user cart
    for session_item in cart_session.items.all():
        cart_item, item_created = CartItem.objects.get_or_create(
            cart=user_cart,
            product=session_item.product,
            variant=session_item.variant,
            defaults={'quantity': session_item.quantity}
        )
        
        if not item_created:
            cart_item.quantity += session_item.quantity
            cart_item.save()
    
    # Delete session cart
    cart_session.delete()
    
    cart_serializer = CartSerializer(user_cart)
    return Response(cart_serializer.data, status=status.HTTP_200_OK)
