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
from products.models import (
    MainCategory, SubCategory, Category, Product, ProductImage
)

User = get_user_model()

def create_main_categories():
    """Create main categories"""
    print("Creating main categories...")

    main_categories_data = [
        {
            'name': 'Her Boutique',
            'slug': 'her-boutique',
            'page': 'boutique',
            'description': 'Luxury fashion and intimate wear',
            'icon': '👗',
            'order': 1
        },
        {
            'name': 'Her Toys',
            'slug': 'her-toys',
            'page': 'toys',
            'description': 'Adult toys and intimate accessories',
            'icon': '🧸',
            'order': 2
        },
        {
            'name': 'Her Scent',
            'slug': 'her-scent',
            'page': 'scent',
            'description': 'Luxury perfumes and fragrances',
            'icon': '🌸',
            'order': 3
        }
    ]

    created_main_categories = []
    for cat_data in main_categories_data:
        main_cat, created = MainCategory.objects.get_or_create(
            slug=cat_data['slug'],
            defaults=cat_data
        )
        if created:
            created_main_categories.append(main_cat)
            print(f"Created main category: {main_cat.name}")

    return created_main_categories

def create_sub_categories():
    """Create subcategories"""
    print("Creating subcategories...")

    # Get main categories
    try:
        boutique = MainCategory.objects.get(slug='her-boutique')
        toys = MainCategory.objects.get(slug='her-toys')
        scent = MainCategory.objects.get(slug='her-scent')
    except MainCategory.DoesNotExist:
        print("Main categories not found, skipping subcategories")
        return

    sub_categories_data = [
        # Boutique subcategories
        {
            'main_category': boutique,
            'name': 'Activewear',
            'slug': 'activewear',
            'description': 'Fitness and activewear',
            'icon': '🏃‍♀️',
            'order': 1
        },
        {
            'main_category': boutique,
            'name': 'Bikinis & Resortwear',
            'slug': 'bikinis-resortwear',
            'description': 'Swimwear and beach fashion',
            'icon': '👙',
            'order': 2
        },
        {
            'main_category': boutique,
            'name': 'Party Dresses',
            'slug': 'party-dresses',
            'description': 'Evening wear and party dresses',
            'icon': '🎉',
            'order': 3
        },
        {
            'main_category': boutique,
            'name': 'Lounge & Bedroom',
            'slug': 'lounge-bedroom',
            'description': 'Comfortable lounge and sleepwear',
            'icon': '🛏️',
            'order': 4
        },
        {
            'main_category': boutique,
            'name': 'Accessories',
            'slug': 'accessories',
            'description': 'Fashion accessories and jewelry',
            'icon': '💎',
            'order': 5
        },
        # Toys subcategories
        {
            'main_category': toys,
            'name': 'Vibrators',
            'slug': 'vibrators',
            'description': 'Electric massagers and vibrators',
            'icon': '⚡',
            'order': 1
        },
        {
            'main_category': toys,
            'name': 'Dildos',
            'slug': 'dildos',
            'description': 'Realistic and fantasy dildos',
            'icon': '🫦',
            'order': 2
        },
        {
            'main_category': toys,
            'name': 'Couples Toys',
            'slug': 'couples-toys',
            'description': 'Toys for couples and partners',
            'icon': '👫',
            'order': 3
        },
        # Scent subcategories
        {
            'main_category': scent,
            'name': 'Floral',
            'slug': 'floral',
            'description': 'Flower-inspired fragrances',
            'icon': '🌸',
            'order': 1
        },
        {
            'main_category': scent,
            'name': 'Oriental',
            'slug': 'oriental',
            'description': 'Warm and spicy fragrances',
            'icon': '🌶️',
            'order': 2
        },
        {
            'main_category': scent,
            'name': 'Fresh',
            'slug': 'fresh',
            'description': 'Clean and aquatic fragrances',
            'icon': '💧',
            'order': 3
        }
    ]

    created_sub_categories = []
    for sub_cat_data in sub_categories_data:
        sub_cat, created = SubCategory.objects.get_or_create(
            main_category=sub_cat_data['main_category'],
            slug=sub_cat_data['slug'],
            defaults=sub_cat_data
        )
        if created:
            created_sub_categories.append(sub_cat)
            print(f"Created subcategory: {sub_cat.name}")

    return created_sub_categories

def create_sample_products():
    """Create sample products"""
    print("Creating sample products...")

    try:
        # Get categories
        activewear = SubCategory.objects.get(slug='activewear')
        bikinis = SubCategory.objects.get(slug='bikinis-resortwear')
        party_dresses = SubCategory.objects.get(slug='party-dresses')
        lounge = SubCategory.objects.get(slug='lounge-bedroom')
        accessories = SubCategory.objects.get(slug='accessories')

        vibrators = SubCategory.objects.get(slug='vibrators')
        floral = SubCategory.objects.get(slug='floral')

    except SubCategory.DoesNotExist:
        print("Subcategories not found, skipping products")
        return

    products_data = [
        {
            'name': 'Active Yoga Set',
            'sub_category': activewear,
            'price': Decimal('4500.00'),
            'description': 'Comfortable and stylish yoga activewear set',
            'short_description': 'Perfect for yoga and fitness activities'
        },
        {
            'name': 'Bikini Top & Bottom',
            'sub_category': bikinis,
            'price': Decimal('3200.00'),
            'description': 'Elegant bikini set for beach and pool',
            'short_description': 'Stylish swimwear for all occasions'
        },
        {
            'name': 'Party Dress',
            'sub_category': party_dresses,
            'price': Decimal('8500.00'),
            'description': 'Glamorous party dress for special occasions',
            'short_description': 'Make a statement at your next event'
        },
        {
            'name': 'Lounge Set',
            'sub_category': lounge,
            'price': Decimal('2800.00'),
            'description': 'Comfortable lounge wear for relaxation',
            'short_description': 'Ultimate comfort for home'
        },
        {
            'name': 'Luxury Necklace',
            'sub_category': accessories,
            'price': Decimal('12000.00'),
            'description': 'Elegant jewelry piece to complement any outfit',
            'short_description': 'Add sophistication to your look'
        },
        {
            'name': 'Personal Massager',
            'sub_category': vibrators,
            'price': Decimal('6500.00'),
            'description': 'High-quality personal massager for intimate moments',
            'short_description': 'Discreet and powerful'
        },
        {
            'name': 'Floral Perfume',
            'sub_category': floral,
            'price': Decimal('4200.00'),
            'description': 'Delicate floral fragrance for everyday wear',
            'short_description': 'Light and feminine scent'
        }
    ]

    created_products = []
    for product_data in products_data:
        product, created = Product.objects.get_or_create(
            name=product_data['name'],
            defaults={
                'slug': slugify(product_data['name']),
                'description': product_data['description'],
                'short_description': product_data['short_description'],
                'sub_category': product_data['sub_category'],
                'main_category': product_data['sub_category'].main_category,
                'price': product_data['price'],
                'stock_quantity': 10,
                'is_active': True,
                'is_featured': True
            }
        )
        if created:
            created_products.append(product)
            print(f"Created product: {product.name}")

    return created_products

if __name__ == '__main__':
    print("Starting data seeding...")

    try:
        create_main_categories()
        create_sub_categories()
        create_sample_products()

        print("Data seeding completed successfully!")

    except Exception as e:
        print(f"Error during data seeding: {e}")
        import traceback
        traceback.print_exc()