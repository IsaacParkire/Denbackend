#!/usr/bin/env python
"""
Django Backend Setup Verification Script
Run this script to test if all components are working correctly.
"""

import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
django.setup()

def test_models():
    """Test if all models can be imported successfully"""
    try:
        from accounts.models import User, UserProfile
        from products.models import Category, Product, ProductVariant, ProductImage, Review, Wishlist
        from services.models import ServiceCategory, Therapist, Service, ServicePackage, ServiceAddon
        from appointments.models import Booking, TimeSlot, BookingCancellation
        from orders.models import Order, OrderItem, ServiceOrder, Coupon
        from payments.models import Payment, PaymentMethod, Transaction
        from cart.models import Cart, CartItem, SavedItem
        
        print("✅ All models imported successfully")
        return True
    except Exception as e:
        print(f"❌ Model import error: {e}")
        return False

def test_serializers():
    """Test if all serializers can be imported successfully"""
    try:
        from accounts.serializers import UserSerializer, UserProfileSerializer
        from products.serializers import CategorySerializer, ProductDetailSerializer
        from services.serializers import ServiceSerializer, TherapistSerializer
        from appointments.serializers import BookingSerializer
        from orders.serializers import OrderSerializer
        from payments.serializers import PaymentSerializer
        from cart.serializers import CartSerializer
        
        print("✅ All serializers imported successfully")
        return True
    except Exception as e:
        print(f"❌ Serializer import error: {e}")
        return False

def test_views():
    """Test if all views can be imported successfully"""
    try:
        from accounts.views import UserRegistrationView, UserLoginView
        from products.views import CategoryListView, ProductListView
        from services.views import ServiceListView, TherapistListView
        from appointments.views import BookingListView
        from orders.views import OrderListView
        from payments.views import PaymentListView
        from cart.views import CartView
        
        print("✅ All views imported successfully")
        return True
    except Exception as e:
        print(f"❌ View import error: {e}")
        return False

def test_admin():
    """Test if all admin configurations are working"""
    try:
        from django.contrib import admin
        from accounts.admin import UserAdmin
        from products.admin import CategoryAdmin, ProductAdmin
        from services.admin import ServiceAdmin, TherapistAdmin
        from appointments.admin import BookingAdmin
        from orders.admin import OrderAdmin
        from payments.admin import PaymentAdmin
        
        print("✅ All admin configurations imported successfully")
        return True
    except Exception as e:
        print(f"❌ Admin import error: {e}")
        return False

def test_urls():
    """Test if all URL configurations are working"""
    try:
        from django.urls import reverse
        from django.test import Client
        
        client = Client()
        # Test a simple endpoint
        response = client.get('/admin/')
        print(f"✅ URL routing working (Admin accessible: {response.status_code})")
        return True
    except Exception as e:
        print(f"❌ URL configuration error: {e}")
        return False

def main():
    """Run all tests"""
    print("🚀 Starting Django Backend Verification...")
    print("=" * 50)
    
    tests = [
        test_models,
        test_serializers,
        test_views,
        test_admin,
        test_urls
    ]
    
    results = []
    for test in tests:
        results.append(test())
        print()
    
    if all(results):
        print("🎉 All tests passed! Your Django backend is ready!")
        print("\nNext steps:")
        print("1. Run: python manage.py runserver")
        print("2. Visit: http://127.0.0.1:8000/admin/ (Admin panel)")
        print("3. API Documentation: http://127.0.0.1:8000/api/")
    else:
        print("❌ Some tests failed. Please check the errors above.")

if __name__ == "__main__":
    main()
