#!/usr/bin/env python
"""
Django data seeding script for Laydies Den
Populates the database with sample data for testing and development
"""

import os
import sys
import django
from decimal import Decimal
from datetime import datetime, timedelta
from django.utils import timezone

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product, Category as ProductCategory
from services.models import Service, Category as ServiceCategory, Therapist
from orders.models import Order, OrderItem
from payments.models import Payment, PaymentMethod

User = get_user_model()

def create_users():
    """Create sample users"""
    print("Creating users...")
    
    # Sample customers
    customers_data = [
        {
            'email': 'customer1@example.com',
            'password': 'password123',
            'first_name': 'Sarah',
            'last_name': 'Johnson',
            'phone': '+254700000001',
            'date_of_birth': '1990-05-15'
        },
        {
            'email': 'customer2@example.com',
            'password': 'password123',
            'first_name': 'Maria',
            'last_name': 'Garcia',
            'phone': '+254700000002',
            'date_of_birth': '1985-08-22'
        },
        {
            'email': 'customer3@example.com',
            'password': 'password123',
            'first_name': 'Emma',
            'last_name': 'Wilson',
            'phone': '+254700000003',
            'date_of_birth': '1992-12-10'
        }
    ]
    
    for customer_data in customers_data:
        if not User.objects.filter(email=customer_data['email']).exists():
            user = User.objects.create_user(**customer_data)
            print(f"Created customer: {user.email}")

def create_product_categories():
    """Create product categories"""
    print("Creating product categories...")
    
    categories_data = [
        {'name': 'Lingerie', 'description': 'Luxury intimate wear and lingerie'},
        {'name': 'Accessories', 'description': 'Fashion accessories and jewelry'},
        {'name': 'Toys', 'description': 'Adult toys and intimate accessories'},
        {'name': 'Scents', 'description': 'Perfumes and fragrances'},
        {'name': 'Activewear', 'description': 'Fitness and activewear'},
        {'name': 'Loungewear', 'description': 'Comfortable lounge and sleepwear'},
    ]
    
    for cat_data in categories_data:
        category, created = ProductCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created product category: {category.name}")

def create_products():
    """Create sample products"""
    print("Creating products...")
    
    # Get categories
    try:
        lingerie_cat = ProductCategory.objects.get(name='Lingerie')
        accessories_cat = ProductCategory.objects.get(name='Accessories')
        toys_cat = ProductCategory.objects.get(name='Toys')
        scents_cat = ProductCategory.objects.get(name='Scents')
    except ProductCategory.DoesNotExist:
        print("Categories not found, skipping products")
        return
    
    products_data = [
        {
            'name': 'Silk Seduction Robe',
            'description': 'Luxurious silk robe with intricate lace detailing. Perfect for intimate moments.',
            'price': Decimal('18900.00'),
            'category': lingerie_cat,
            'stock_quantity': 25,
            'is_featured': True,
        },
        {
            'name': 'Elegant Lace Teddy',
            'description': 'Sophisticated lace teddy with adjustable straps and delicate embroidery.',
            'price': Decimal('12500.00'),
            'category': lingerie_cat,
            'stock_quantity': 30,
            'is_featured': True,
        },
        {
            'name': 'Designer Pearl Necklace',
            'description': 'Elegant pearl necklace perfect for special occasions.',
            'price': Decimal('45000.00'),
            'category': accessories_cat,
            'stock_quantity': 15,
            'is_featured': False,
        },
        {
            'name': 'Luxury Massage Oil Set',
            'description': 'Premium massage oil collection with exotic scents.',
            'price': Decimal('8500.00'),
            'category': toys_cat,
            'stock_quantity': 40,
            'is_featured': True,
        },
        {
            'name': 'French Perfume Collection',
            'description': 'Exclusive collection of French perfumes with captivating fragrances.',
            'price': Decimal('25000.00'),
            'category': scents_cat,
            'stock_quantity': 20,
            'is_featured': True,
        }
    ]
    
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            print(f"Created product: {product.name}")

def create_service_categories():
    """Create service categories"""
    print("Creating service categories...")
    
    categories_data = [
        {'name': 'Massage Therapy', 'description': 'Professional massage and wellness services'},
        {'name': 'Personal Training', 'description': 'Fitness and personal training services'},
        {'name': 'Lifestyle Consulting', 'description': 'Personal lifestyle and wellness consulting'},
        {'name': 'Beauty Services', 'description': 'Beauty and grooming services'},
    ]
    
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            print(f"Created service category: {category.name}")

def create_therapists():
    """Create sample therapists"""
    print("Creating therapists...")
    
    therapists_data = [
        {
            'name': 'Marcus Thompson',
            'specialties': 'Deep tissue massage, Sports therapy',
            'experience_years': 8,
            'bio': 'Professional massage therapist with 8 years of experience in therapeutic and relaxation massage.',
            'hourly_rate': Decimal('5500.00'),
            'is_available': True
        },
        {
            'name': 'David Rodriguez',
            'specialties': 'Personal training, Fitness coaching',
            'experience_years': 6,
            'bio': 'Certified personal trainer specializing in strength training and wellness coaching.',
            'hourly_rate': Decimal('4500.00'),
            'is_available': True
        },
        {
            'name': 'James Anderson',
            'specialties': 'Lifestyle consulting, Wellness coaching',
            'experience_years': 10,
            'bio': 'Experienced lifestyle consultant helping clients achieve their wellness goals.',
            'hourly_rate': Decimal('6000.00'),
            'is_available': True
        }
    ]
    
    for therapist_data in therapists_data:
        therapist, created = Therapist.objects.get_or_create(
            name=therapist_data['name'],
            defaults=therapist_data
        )
        if created:
            print(f"Created therapist: {therapist.name}")

def create_services():
    """Create sample services"""
    print("Creating services...")
    
    try:
        # Get categories and therapists
        massage_cat = ServiceCategory.objects.get(name='Massage Therapy')
        training_cat = ServiceCategory.objects.get(name='Personal Training')
        lifestyle_cat = ServiceCategory.objects.get(name='Lifestyle Consulting')
        
        marcus = Therapist.objects.get(name='Marcus Thompson')
        david = Therapist.objects.get(name='David Rodriguez')
        james = Therapist.objects.get(name='James Anderson')
    except (ServiceCategory.DoesNotExist, Therapist.DoesNotExist):
        print("Categories or therapists not found, skipping services")
        return
    
    services_data = [
        {
            'name': 'Relaxation Massage',
            'description': 'Full body relaxation massage with premium oils and techniques.',
            'category': massage_cat,
            'duration': 60,
            'price': Decimal('8500.00'),
            'is_active': True,
            'max_participants': 1
        },
        {
            'name': 'Deep Tissue Massage',
            'description': 'Therapeutic deep tissue massage for muscle tension relief.',
            'category': massage_cat,
            'duration': 90,
            'price': Decimal('12000.00'),
            'is_active': True,
            'max_participants': 1
        },
        {
            'name': 'Personal Training Session',
            'description': 'One-on-one fitness training session customized to your goals.',
            'category': training_cat,
            'duration': 60,
            'price': Decimal('6500.00'),
            'is_active': True,
            'max_participants': 1
        }
    ]
    
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            print(f"Created service: {service.name}")
            
            # Assign therapists
            if 'Massage' in service.name:
                service.therapists.add(marcus)
            elif 'Training' in service.name:
                service.therapists.add(david)

def create_payment_methods():
    """Create payment methods"""
    print("Creating payment methods...")
    
    methods_data = [
        {'name': 'M-Pesa', 'is_active': True},
        {'name': 'Credit Card', 'is_active': True},
        {'name': 'Bank Transfer', 'is_active': True},
        {'name': 'Cash', 'is_active': True},
    ]
    
    for method_data in methods_data:
        method, created = PaymentMethod.objects.get_or_create(
            name=method_data['name'],
            defaults=method_data
        )
        if created:
            print(f"Created payment method: {method.name}")

def main():
    """Main function to run all seeding operations"""
    print("Starting database seeding...")
    
    try:
        create_users()
        create_product_categories()
        create_products()
        create_service_categories()
        create_therapists()
        create_services()
        create_payment_methods()
        
        print("\n✅ Database seeding completed successfully!")
        print("\nSample data created:")
        print(f"- Users: {User.objects.count()}")
        print(f"- Product Categories: {ProductCategory.objects.count()}")
        print(f"- Products: {Product.objects.count()}")
        print(f"- Service Categories: {ServiceCategory.objects.count()}")
        print(f"- Services: {Service.objects.count()}")
        print(f"- Therapists: {Therapist.objects.count()}")
        print(f"- Payment Methods: {PaymentMethod.objects.count()}")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == '__main__':
    main()
