from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from django_filters.rest_framework import DjangoFilterBackend
from rest_framework.filters import SearchFilter, OrderingFilter
from .models import MainCategory, SubCategory, Category, Product, ProductReview, Wishlist
from .serializers import (
    MainCategorySerializer,
    SubCategorySerializer, 
    CategorySerializer, 
    ProductListSerializer, 
    ProductDetailSerializer,
    ProductReviewSerializer,
    WishlistSerializer
)

class MainCategoryListView(generics.ListAPIView):
    queryset = MainCategory.objects.filter(is_active=True).order_by('page', 'order', 'name')
    serializer_class = MainCategorySerializer
    permission_classes = [permissions.AllowAny]

class SubCategoryListView(generics.ListAPIView):
    serializer_class = SubCategorySerializer
    permission_classes = [permissions.AllowAny]
    
    def get_queryset(self):
        main_category_id = self.request.query_params.get('main_category')
        page = self.request.query_params.get('page')
        
        queryset = SubCategory.objects.filter(is_active=True)
        
        if main_category_id:
            queryset = queryset.filter(main_category_id=main_category_id)
        
        if page:
            queryset = queryset.filter(main_category__page=page)
            
        return queryset.order_by('main_category__order', 'order', 'name')

class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.filter(is_active=True)
    serializer_class = CategorySerializer
    permission_classes = [permissions.AllowAny]

class ProductListView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]
    filter_backends = [DjangoFilterBackend, SearchFilter, OrderingFilter]
    filterset_fields = [
        'category', 'main_category', 'sub_category', 'sub_category__slug', 'main_category__page',
        'is_featured', 'is_digital', 'is_exclusive', 'is_limited_edition', 
        'is_bestseller', 'is_new_arrival'
    ]
    search_fields = ['name', 'description', 'short_description', 'sku']
    ordering_fields = ['name', 'price', 'created_at']
    ordering = ['-created_at']

class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductDetailSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'slug'

class FeaturedProductsView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True, is_featured=True)
    serializer_class = ProductListSerializer
    permission_classes = [permissions.AllowAny]

class ProductReviewListCreateView(generics.ListCreateAPIView):
    serializer_class = ProductReviewSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]
    
    def get_queryset(self):
        product_id = self.kwargs['product_id']
        return ProductReview.objects.filter(product_id=product_id, is_approved=True)
    
    def perform_create(self, serializer):
        product_id = self.kwargs['product_id']
        serializer.save(user=self.request.user, product_id=product_id)

class WishlistView(generics.ListCreateAPIView):
    serializer_class = WishlistSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def create(self, request, *args, **kwargs):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
            wishlist_item, created = Wishlist.objects.get_or_create(
                user=request.user,
                product=product
            )
            if created:
                serializer = self.get_serializer(wishlist_item)
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            else:
                return Response({'message': 'Product already in wishlist'}, 
                              status=status.HTTP_200_OK)
        except Product.DoesNotExist:
            return Response({'error': 'Product not found'}, 
                          status=status.HTTP_404_NOT_FOUND)

class WishlistRemoveView(generics.DestroyAPIView):
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return Wishlist.objects.filter(user=self.request.user)
    
    def destroy(self, request, *args, **kwargs):
        product_id = kwargs.get('product_id')
        try:
            wishlist_item = Wishlist.objects.get(
                user=request.user,
                product_id=product_id
            )
            wishlist_item.delete()
            return Response({'message': 'Product removed from wishlist'})
        except Wishlist.DoesNotExist:
            return Response({'error': 'Product not in wishlist'}, 
                          status=status.HTTP_404_NOT_FOUND)

@api_view(['GET'])
@permission_classes([permissions.AllowAny])
def product_search(request):
    query = request.GET.get('q', '')
    category = request.GET.get('category', '')
    min_price = request.GET.get('min_price', '')
    max_price = request.GET.get('max_price', '')
    
    products = Product.objects.filter(is_active=True)
    
    if query:
        products = products.filter(name__icontains=query)
    
    if category:
        products = products.filter(category__slug=category)
    
    if min_price:
        products = products.filter(price__gte=min_price)
    
    if max_price:
        products = products.filter(price__lte=max_price)
    
    serializer = ProductListSerializer(products, many=True, context={'request': request})
    return Response(serializer.data)