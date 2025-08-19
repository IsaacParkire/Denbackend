# Script to create a superuser for Django admin
import os
import django
import sys
from pathlib import Path

# Add the backend directory to the Python path
backend_dir = Path(__file__).resolve().parent
sys.path.append(str(backend_dir))

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
django.setup()

from django.contrib.auth import get_user_model

User = get_user_model()

def create_superuser():
    if not User.objects.filter(is_superuser=True).exists():
        User.objects.create_superuser(
            email='admin@laydiesden.com',
            password='admin123',
            first_name='Admin',
            last_name='User'
        )
        print("Superuser created successfully!")
        print("Email: admin@laydiesden.com")
        print("Password: admin123")
    else:
        print("Superuser already exists!")

if __name__ == "__main__":
    create_superuser()
