from django.core.management.base import BaseCommand
from products.models import ProductImage

class Command(BaseCommand):
    help = 'Delete all product images from the database and Uploadcare'

    def handle(self, *args, **options):
        images = ProductImage.objects.all()
        count = images.count()
        if count == 0:
            self.stdout.write(self.style.SUCCESS('No product images to delete.'))
            return
        
        self.stdout.write(f'Deleting {count} product images...')
        images.delete()  # This will call the delete method on each instance
        self.stdout.write(self.style.SUCCESS(f'Successfully deleted {count} product images.'))