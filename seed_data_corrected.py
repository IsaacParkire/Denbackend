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
from django.utils.text import slugify

# Setup Django
sys.path.append(os.path.dirname(os.path.abspath(__file__)))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
django.setup()

from django.contrib.auth import get_user_model
from products.models import Product, Category
from services.models import Service, ServiceCategory, Therapist

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
        },
        {
            'email': 'customer2@example.com',
            'password': 'password123',
            'first_name': 'Maria',
            'last_name': 'Garcia',
        },
        {
            'email': 'customer3@example.com',
            'password': 'password123',
            'first_name': 'Emma',
            'last_name': 'Wilson',
        }
    ]
    
    created_users = []
    for customer_data in customers_data:
        if not User.objects.filter(email=customer_data['email']).exists():
            user = User.objects.create_user(**customer_data)
            created_users.append(user)
            print(f"Created customer: {user.email}")
    
    return created_users

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
    
    created_categories = []
    for cat_data in categories_data:
        slug = slugify(cat_data['name'])
        category, created = Category.objects.get_or_create(
            name=cat_data['name'],
            defaults={
                'description': cat_data['description'],
                'slug': slug
            }
        )
        if created:
            created_categories.append(category)
            print(f"Created product category: {category.name}")
    
    return created_categories

def create_products():
    """Create sample products"""
    print("Creating products...")
    
    # Get categories
    try:
        lingerie_cat = Category.objects.get(name='Lingerie')
        accessories_cat = Category.objects.get(name='Accessories')
        toys_cat = Category.objects.get(name='Toys')
        scents_cat = Category.objects.get(name='Scents')
    except Category.DoesNotExist:
        print("Categories not found, skipping products")
        return []
    
    products_data = [
        {
            'name': 'Silk Seduction Robe',
            'description': 'Luxurious silk robe with intricate lace detailing. Perfect for intimate moments.',
            'short_description': 'Luxurious silk robe with lace detailing',
            'price': Decimal('18900.00'),
            'category': lingerie_cat,
            'stock_quantity': 25,
            'is_featured': True,
            'sku': 'SSR001'
        },
        {
            'name': 'Elegant Lace Teddy',
            'description': 'Sophisticated lace teddy with adjustable straps and delicate embroidery.',
            'short_description': 'Sophisticated lace teddy with adjustable straps',
            'price': Decimal('12500.00'),
            'category': lingerie_cat,
            'stock_quantity': 30,
            'is_featured': True,
            'sku': 'ELT001'
        },
        {
            'name': 'Designer Pearl Necklace',
            'description': 'Elegant pearl necklace perfect for special occasions.',
            'short_description': 'Elegant pearl necklace for special occasions',
            'price': Decimal('45000.00'),
            'category': accessories_cat,
            'stock_quantity': 15,
            'is_featured': False,
            'sku': 'DPN001'
        },
        {
            'name': 'Luxury Massage Oil Set',
            'description': 'Premium massage oil collection with exotic scents.',
            'short_description': 'Premium massage oil collection',
            'price': Decimal('8500.00'),
            'category': toys_cat,
            'stock_quantity': 40,
            'is_featured': True,
            'sku': 'LMOS001'
        },
        {
            'name': 'French Perfume Collection',
            'description': 'Exclusive collection of French perfumes with captivating fragrances.',
            'short_description': 'Exclusive French perfume collection',
            'price': Decimal('25000.00'),
            'category': scents_cat,
            'stock_quantity': 20,
            'is_featured': True,
            'sku': 'FPC001'
        }
    ]
    
    created_products = []
    for product_data in products_data:
        # Create slug from name
        product_data['slug'] = slugify(product_data['name'])
        
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults=product_data
        )
        if created:
            created_products.append(product)
            print(f"Created product: {product.name}")
    
    return created_products

def create_service_categories():
    """Create service categories"""
    print("Creating service categories...")
    
    categories_data = [
        {'name': 'Massage Therapy', 'description': 'Professional massage and wellness services'},
        {'name': 'Personal Training', 'description': 'Fitness and personal training services'},
        {'name': 'Lifestyle Consulting', 'description': 'Personal lifestyle and wellness consulting'},
        {'name': 'Beauty Services', 'description': 'Beauty and grooming services'},
    ]
    
    created_categories = []
    for cat_data in categories_data:
        category, created = ServiceCategory.objects.get_or_create(
            name=cat_data['name'],
            defaults={'description': cat_data['description']}
        )
        if created:
            created_categories.append(category)
            print(f"Created service category: {category.name}")
    
    return created_categories

def create_therapists():
    """Create sample therapists"""
    print("Creating therapists...")
    
    # Create therapist users first
    therapist_users_data = [
        {
            'email': 'marcus@laydiesden.com',
            'password': 'therapist123',
            'first_name': 'Marcus',
            'last_name': 'Thompson',
        },
        {
            'email': 'david@laydiesden.com',
            'password': 'therapist123',
            'first_name': 'David',
            'last_name': 'Rodriguez',
        },
        {
            'email': 'james@laydiesden.com',
            'password': 'therapist123',
            'first_name': 'James',
            'last_name': 'Anderson',
        }
    ]
    
    therapist_users = []
    for user_data in therapist_users_data:
        if not User.objects.filter(email=user_data['email']).exists():
            user = User.objects.create_user(**user_data)
            therapist_users.append(user)
            print(f"Created therapist user: {user.email}")
    
    # Create therapist profiles
    therapists_data = [
        {
            'user': therapist_users[0] if therapist_users else User.objects.get(email='marcus@laydiesden.com'),
            'bio': 'Professional massage therapist with 8 years of experience in therapeutic and relaxation massage.',
            'experience_years': 8,
            'hourly_rate': Decimal('5500.00'),
            'is_available': True
        },
        {
            'user': therapist_users[1] if len(therapist_users) > 1 else User.objects.get(email='david@laydiesden.com'),
            'bio': 'Certified personal trainer specializing in strength training and wellness coaching.',
            'experience_years': 6,
            'hourly_rate': Decimal('4500.00'),
            'is_available': True
        },
        {
            'user': therapist_users[2] if len(therapist_users) > 2 else User.objects.get(email='james@laydiesden.com'),
            'bio': 'Experienced lifestyle consultant helping clients achieve their wellness goals.',
            'experience_years': 10,
            'hourly_rate': Decimal('6000.00'),
            'is_available': True
        }
    ]
    
    created_therapists = []
    for therapist_data in therapists_data:
        therapist, created = Therapist.objects.get_or_create(
            user=therapist_data['user'],
            defaults=therapist_data
        )
        if created:
            created_therapists.append(therapist)
            print(f"Created therapist: {therapist.user.get_full_name()}")
    
    return created_therapists

def create_services():
    """Create sample services"""
    print("Creating services...")
    
    try:
        # Get categories
        massage_cat = ServiceCategory.objects.get(name='Massage Therapy')
        training_cat = ServiceCategory.objects.get(name='Personal Training')
        lifestyle_cat = ServiceCategory.objects.get(name='Lifestyle Consulting')
    except ServiceCategory.DoesNotExist:
        print("Service categories not found, skipping services")
        return []
    
    services_data = [
        {
            'name': 'Relaxation Massage',
            'description': 'Full body relaxation massage with premium oils and techniques.',
            'category': massage_cat,
            'duration': 60,
            'price': Decimal('8500.00'),
            'is_active': True,
        },
        {
            'name': 'Deep Tissue Massage',
            'description': 'Therapeutic deep tissue massage for muscle tension relief.',
            'category': massage_cat,
            'duration': 90,
            'price': Decimal('12000.00'),
            'is_active': True,
        },
        {
            'name': 'Personal Training Session',
            'description': 'One-on-one fitness training session customized to your goals.',
            'category': training_cat,
            'duration': 60,
            'price': Decimal('6500.00'),
            'is_active': True,
        },
        {
            'name': 'Lifestyle Consultation',
            'description': 'Comprehensive lifestyle and wellness consultation session.',
            'category': lifestyle_cat,
            'duration': 120,
            'price': Decimal('8000.00'),
            'is_active': True,
        }
    ]
    
    created_services = []
    for service_data in services_data:
        service, created = Service.objects.get_or_create(
            name=service_data['name'],
            defaults=service_data
        )
        if created:
            created_services.append(service)
            print(f"Created service: {service.name}")
    
    return created_services

def main():
    """Main function to run all seeding operations"""
    print("🌱 Starting database seeding for Laydies Den...")
    print("=" * 50)
    
    try:
        users = create_users()
        product_categories = create_product_categories()
        products = create_products()
        service_categories = create_service_categories()
        therapists = create_therapists()
        services = create_services()
        
        print("\n" + "=" * 50)
        print("✅ Database seeding completed successfully!")
        print("\n📊 Summary of created data:")
        print(f"👥 Users: {User.objects.count()}")
        print(f"📦 Product Categories: {Category.objects.count()}")
        print(f"🛍️  Products: {Product.objects.count()}")
        print(f"🔧 Service Categories: {ServiceCategory.objects.count()}")
        print(f"💆 Services: {Service.objects.count()}")
        print(f"👨‍⚕️ Therapists: {Therapist.objects.count()}")
        print("\n🎉 Your Laydies Den database is now ready for development!")
        
    except Exception as e:
        print(f"❌ Error during seeding: {str(e)}")
        import traceback
        traceback.print_exc()
        return False
    
    return True

if __name__ == '__main__':
    success = main()
    sys.exit(0 if success else 1)
