#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'laydies_backend.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc

    # --- AUTO CREATE SUPERUSER (Render free plan fix) ---
    import django
    django.setup()
    from django.contrib.auth import get_user_model

    User = get_user_model()
    username = os.environ.get("DJANGO_SUPERUSER_USERNAME")
    email = os.environ.get("DJANGO_SUPERUSER_EMAIL")
    password = os.environ.get("DJANGO_SUPERUSER_PASSWORD")

    if username and email and password:
        if not User.objects.filter(username=username).exists():
            print("Creating superuser...")
            User.objects.create_superuser(username=username, email=email, password=password)
        else:
            print("Superuser already exists")

    # --- Continue normal Django execution ---
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
