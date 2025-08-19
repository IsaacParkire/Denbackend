from django.core.management.base import BaseCommand
from products.models import MainCategory, SubCategory

class Command(BaseCommand):
    help = 'Populate main categories and subcategories for the Laydies Den website'

    def handle(self, *args, **options):
        self.stdout.write(self.style.SUCCESS('Creating main categories and subcategories...'))

        # Define the category structure
        categories_data = {
            'boutique': {
                'name': 'Her Boutique',
                'icon': '👗',
                'description': 'Luxury fashion and intimate wear collection',
                'subcategories': [
                    {'name': 'Activewear', 'slug': 'activewear', 'icon': '🏃‍♀️'},
                    {'name': 'Bikinis & Resortwear', 'slug': 'bikinis', 'icon': '👙'},
                    {'name': 'Party Dresses', 'slug': 'party', 'icon': '🎉'},
                    {'name': 'Lounge & Bedroom', 'slug': 'lounge', 'icon': '🛏️'},
                    {'name': 'Accessories', 'slug': 'accessories', 'icon': '💎'},
                ]
            },
            'toys': {
                'name': 'Her Toys',
                'icon': '✨',
                'description': 'Premium intimate wellness products',
                'subcategories': [
                    {'name': 'Luxury Collection', 'slug': 'luxury', 'icon': '💎'},
                    {'name': 'For Couples', 'slug': 'couples', 'icon': '💕'},
                    {'name': 'Wellness & Care', 'slug': 'wellness', 'icon': '🌸'},
                    {'name': 'Accessories', 'slug': 'accessories', 'icon': '🎀'},
                    {'name': 'Limited Edition', 'slug': 'limited', 'icon': '👑'},
                ]
            },
            'scent': {
                'name': 'Her Scent',
                'icon': '🌸',
                'description': 'Exclusive fragrances and perfumes',
                'subcategories': [
                    {'name': 'Signature Collection', 'slug': 'signature', 'icon': '👑'},
                    {'name': 'Exotic Blends', 'slug': 'exotic', 'icon': '🌺'},
                    {'name': 'Aphrodisiac', 'slug': 'aphrodisiac', 'icon': '💋'},
                    {'name': 'Custom Blends', 'slug': 'custom', 'icon': '🎨'},
                    {'name': 'Essential Oils', 'slug': 'oils', 'icon': '🌿'},
                ]
            }
        }

        created_count = 0
        subcategory_count = 0

        for page_key, data in categories_data.items():
            # Create or get main category
            main_category, created = MainCategory.objects.get_or_create(
                slug=data['name'].lower().replace(' ', '-'),
                defaults={
                    'name': data['name'],
                    'page': page_key,
                    'icon': data['icon'],
                    'description': data['description'],
                    'is_active': True,
                    'order': list(categories_data.keys()).index(page_key)
                }
            )
            
            if created:
                created_count += 1
                self.stdout.write(f'  Created main category: {main_category.name}')
            else:
                self.stdout.write(f'  Main category exists: {main_category.name}')

            # Create subcategories
            for i, sub_data in enumerate(data['subcategories']):
                subcategory, sub_created = SubCategory.objects.get_or_create(
                    main_category=main_category,
                    slug=sub_data['slug'],
                    defaults={
                        'name': sub_data['name'],
                        'icon': sub_data['icon'],
                        'is_active': True,
                        'order': i
                    }
                )
                
                if sub_created:
                    subcategory_count += 1
                    self.stdout.write(f'    Created subcategory: {subcategory.name}')
                else:
                    self.stdout.write(f'    Subcategory exists: {subcategory.name}')

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created {created_count} main categories and {subcategory_count} subcategories'
            )
        )
            slug='her-boutique',
            defaults={
                'name': 'Her Boutique',
                'page': 'boutique',
                'description': 'Luxury fashion, intimate wear, and accessories designed for the modern woman',
                'icon': '👗',
                'order': 1
            }
        )
        
        boutique_subcategories = [
            {'name': 'All Items', 'slug': 'all-items', 'icon': '👗', 'order': 1},
            {'name': 'Activewear', 'slug': 'activewear', 'icon': '🏃‍♀️', 'order': 2},
            {'name': 'Bikinis & Resortwear', 'slug': 'bikinis-resortwear', 'icon': '👙', 'order': 3},
            {'name': 'Party Dresses', 'slug': 'party-dresses', 'icon': '🎉', 'order': 4},
            {'name': 'Lounge & Bedroom', 'slug': 'lounge-bedroom', 'icon': '🛏️', 'order': 5},
            {'name': 'Accessories', 'slug': 'accessories', 'icon': '💎', 'order': 6},
        ]
        
        for subcat in boutique_subcategories:
            SubCategory.objects.get_or_create(
                main_category=boutique_main,
                slug=subcat['slug'],
                defaults={
                    'name': subcat['name'],
                    'icon': subcat['icon'],
                    'order': subcat['order']
                }
            )

        # Her Toys categories
        toys_main, created = MainCategory.objects.get_or_create(
            slug='her-toys',
            defaults={
                'name': 'Her Toys',
                'page': 'toys',
                'description': 'Premium intimate wellness products for personal exploration',
                'icon': '🎭',
                'order': 2
            }
        )
        
        toys_subcategories = [
            {'name': 'All Products', 'slug': 'all-products', 'icon': '✨', 'order': 1},
            {'name': 'Luxury Collection', 'slug': 'luxury-collection', 'icon': '💎', 'order': 2},
            {'name': 'For Couples', 'slug': 'for-couples', 'icon': '💕', 'order': 3},
            {'name': 'Wellness & Care', 'slug': 'wellness-care', 'icon': '🌸', 'order': 4},
            {'name': 'Accessories', 'slug': 'toys-accessories', 'icon': '🎀', 'order': 5},
            {'name': 'Limited Edition', 'slug': 'limited-edition', 'icon': '👑', 'order': 6},
        ]
        
        for subcat in toys_subcategories:
            SubCategory.objects.get_or_create(
                main_category=toys_main,
                slug=subcat['slug'],
                defaults={
                    'name': subcat['name'],
                    'icon': subcat['icon'],
                    'order': subcat['order']
                }
            )

        # Her Scent categories
        scent_main, created = MainCategory.objects.get_or_create(
            slug='her-scent',
            defaults={
                'name': 'Her Scent',
                'page': 'scent',
                'description': 'Luxury fragrances and essential oils for every occasion',
                'icon': '🌸',
                'order': 3
            }
        )
        
        scent_subcategories = [
            {'name': 'All Fragrances', 'slug': 'all-fragrances', 'icon': '✨', 'order': 1},
            {'name': 'Signature Collection', 'slug': 'signature-collection', 'icon': '👑', 'order': 2},
            {'name': 'Exotic Blends', 'slug': 'exotic-blends', 'icon': '🌺', 'order': 3},
            {'name': 'Aphrodisiac', 'slug': 'aphrodisiac', 'icon': '💋', 'order': 4},
            {'name': 'Custom Blends', 'slug': 'custom-blends', 'icon': '🎨', 'order': 5},
            {'name': 'Essential Oils', 'slug': 'essential-oils', 'icon': '🌿', 'order': 6},
        ]
        
        for subcat in scent_subcategories:
            SubCategory.objects.get_or_create(
                main_category=scent_main,
                slug=subcat['slug'],
                defaults={
                    'name': subcat['name'],
                    'icon': subcat['icon'],
                    'order': subcat['order']
                }
            )

        self.stdout.write(
            self.style.SUCCESS(
                f'Successfully created categories:\n'
                f'- {boutique_main.name}: {boutique_main.subcategories.count()} subcategories\n'
                f'- {toys_main.name}: {toys_main.subcategories.count()} subcategories\n'
                f'- {scent_main.name}: {scent_main.subcategories.count()} subcategories'
            )
        )
