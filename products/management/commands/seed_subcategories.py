#!/usr/bin/env python
"""
Django management command to properly seed subcategories
"""

import os
import sys
import django
from django.core.management.base import BaseCommand

# Setup Django
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
django.setup()

from products.models import MainCategory, SubCategory

class Command(BaseCommand):
    help = 'Properly seed subcategories for each main category'

    def handle(self, *args, **options):
        self.stdout.write('Seeding proper subcategories...')

        # Define proper subcategories for each main category
        subcategory_data = {
            'boutique': [
                {'name': 'Activewear', 'slug': 'activewear', 'icon': '🏃‍♀️', 'description': 'Fitness and activewear'},
                {'name': 'Bikinis & Resortwear', 'slug': 'bikinis-resortwear', 'icon': '👙', 'description': 'Swimwear and beach fashion'},
                {'name': 'Party Dresses', 'slug': 'party-dresses', 'icon': '🎉', 'description': 'Evening wear and party dresses'},
                {'name': 'Lounge & Bedroom', 'slug': 'lounge-bedroom', 'icon': '🛏️', 'description': 'Comfortable lounge and sleepwear'},
                {'name': 'Accessories', 'slug': 'accessories', 'icon': '💎', 'description': 'Fashion accessories and jewelry'},
            ],
            'toys': [
                {'name': 'Vibrators', 'slug': 'vibrators', 'icon': '⚡', 'description': 'Electric massagers and vibrators'},
                {'name': 'Dildos', 'slug': 'dildos', 'icon': '🫦', 'description': 'Realistic and fantasy dildos'},
                {'name': 'Couples Toys', 'slug': 'couples-toys', 'icon': '👫', 'description': 'Toys for couples and partners'},
                {'name': 'Lubricants', 'slug': 'lubricants', 'icon': '💧', 'description': 'Premium lubricants and enhancers'},
                {'name': 'Accessories', 'slug': 'toy-accessories', 'icon': '🎀', 'description': 'Toy accessories and storage'},
            ],
            'scent': [
                {'name': 'Floral', 'slug': 'floral', 'icon': '🌸', 'description': 'Flower-inspired fragrances'},
                {'name': 'Oriental', 'slug': 'oriental', 'icon': '🌶️', 'description': 'Warm and spicy fragrances'},
                {'name': 'Fresh', 'slug': 'fresh', 'icon': '💧', 'description': 'Clean and aquatic fragrances'},
                {'name': 'Woody', 'slug': 'woody', 'icon': '🌲', 'description': 'Earthy and woody scents'},
                {'name': 'Signature', 'slug': 'signature', 'icon': '👑', 'description': 'Our signature fragrance collection'},
            ]
        }

        # Update main category names to be consistent
        main_category_updates = {
            'boutique': 'Her Boutique',
            'toys': 'Her Toys',
            'scent': 'Her Scent'
        }

        for page, display_name in main_category_updates.items():
            try:
                main_cat = MainCategory.objects.get(page=page)
                main_cat.name = display_name
                main_cat.save()
                self.stdout.write(f'Updated main category: {main_cat.name}')
            except MainCategory.DoesNotExist:
                self.stdout.write(f'Warning: Main category with page "{page}" not found')

        # Clear existing subcategories and create new ones
        SubCategory.objects.all().delete()
        self.stdout.write('Cleared existing subcategories')

        order = 1
        for page, subcats in subcategory_data.items():
            try:
                main_cat = MainCategory.objects.get(page=page)
                for subcat_data in subcats:
                    subcat = SubCategory.objects.create(
                        main_category=main_cat,
                        name=subcat_data['name'],
                        slug=subcat_data['slug'],
                        description=subcat_data['description'],
                        icon=subcat_data['icon'],
                        order=order,
                        is_active=True
                    )
                    self.stdout.write(f'Created subcategory: {subcat.name} ({main_cat.name})')
                    order += 1
            except MainCategory.DoesNotExist:
                self.stdout.write(f'Warning: Main category with page "{page}" not found')

        self.stdout.write(self.style.SUCCESS('Successfully seeded subcategories!'))