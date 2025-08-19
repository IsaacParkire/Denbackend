from django.urls import path
from .views import (
    MainCategoryListView,
    SubCategoryListView,
    CategoryListView,
    ProductListView,
    ProductDetailView,
    FeaturedProductsView,
    ProductReviewListCreateView,
    WishlistView,
    WishlistRemoveView,
    product_search
)

urlpatterns = [
    path('main-categories/', MainCategoryListView.as_view(), name='main-category-list'),
    path('sub-categories/', SubCategoryListView.as_view(), name='sub-category-list'),
    path('categories/', CategoryListView.as_view(), name='category-list'),
    path('', ProductListView.as_view(), name='product-list'),
    path('featured/', FeaturedProductsView.as_view(), name='featured-products'),
    path('search/', product_search, name='product-search'),
    path('<slug:slug>/', ProductDetailView.as_view(), name='product-detail'),
    path('<int:product_id>/reviews/', ProductReviewListCreateView.as_view(), name='product-reviews'),
    path('wishlist/', WishlistView.as_view(), name='wishlist'),
    path('wishlist/remove/<int:product_id>/', WishlistRemoveView.as_view(), name='wishlist-remove'),
]