from django.core.management.base import BaseCommand
from accounts.models import MembershipPlan


class Command(BaseCommand):
    help = 'Create initial membership plans based on frontend specifications'

    def handle(self, *args, **options):
        # Basic Plan
        basic_plan, created = MembershipPlan.objects.get_or_create(
            plan_type='basic',
            defaults={
                'name': 'Basic',
                'price': 0.00,
                'currency': 'KSH',
                'duration_months': 1,
                'description': 'Perfect for getting started with our community',
                'her_secrets_access': False,
                'premium_events_access': False,
                'vip_events_access': False,
                'priority_booking': False,
                'premium_gallery_access': False,
                'vip_gallery_access': False,
                'custom_experiences': False,
                'concierge_service': False,
                'private_events': False,
                'features_list': [
                    'Basic access to products and services',
                    'Public events only',
                    'Standard massage and service bookings',
                    'Public album photos',
                    'Community forum access',
                    'Basic customer support'
                ],
                'restrictions_list': [
                    'No access to Her Secrets page',
                    'Limited to public events only',
                    'Standard booking priority',
                    'Basic gallery access only'
                ],
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created Basic membership plan')
        else:
            self.stdout.write(f'Basic membership plan already exists')

        # Premium Plan
        premium_plan, created = MembershipPlan.objects.get_or_create(
            plan_type='premium',
            defaults={
                'name': 'Premium',
                'price': 25000.00,
                'currency': 'KSH',
                'duration_months': 1,
                'description': 'Unlock exclusive experiences and premium content',
                'her_secrets_access': True,
                'premium_events_access': True,
                'vip_events_access': False,
                'priority_booking': True,
                'premium_gallery_access': True,
                'vip_gallery_access': False,
                'custom_experiences': False,
                'concierge_service': False,
                'private_events': False,
                'features_list': [
                    'Access to premium themed nights and Her Secrets',
                    'Priority bookings and early RSVP access',
                    'Access to all public events + select VIP nights',
                    'Premium uncensored gallery access',
                    'More explicit shots and premium dancer profiles',
                    'Access to special themed sessions',
                    'Seasonal packages and exclusive content',
                    'Premium customer support',
                    'Monthly exclusive newsletter'
                ],
                'restrictions_list': [
                    'Limited VIP night access',
                    'Standard VIP amenities only'
                ],
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created Premium membership plan')
        else:
            self.stdout.write(f'Premium membership plan already exists')

        # VIP Elite Plan
        vip_plan, created = MembershipPlan.objects.get_or_create(
            plan_type='vip',
            defaults={
                'name': 'VIP Elite',
                'price': 65000.00,
                'currency': 'KSH',
                'duration_months': 1,
                'description': 'The ultimate luxury experience with exclusive privileges',
                'her_secrets_access': True,
                'premium_events_access': True,
                'vip_events_access': True,
                'priority_booking': True,
                'premium_gallery_access': True,
                'vip_gallery_access': True,
                'custom_experiences': True,
                'concierge_service': True,
                'private_events': True,
                'features_list': [
                    'Guaranteed access to ALL VIP nights and secrets',
                    'Front lounge seats and premium positioning',
                    'Private invitation to inner circle nights',
                    'Priority RSVPs for all events',
                    'VIP-only albums: uncensored, intimate, private photos',
                    'Secret after parties and exclusive gatherings',
                    'Special event creation on request',
                    'Exclusive gifts and early product access',
                    'Exclusive fetish shows and private dancer access',
                    'Custom content and one-on-one experiences',
                    'Complimentary fantasy add-ons',
                    'First pick of masseuse/companion',
                    'Fully tailored sessions',
                    '24/7 VIP concierge service',
                    'Private entrance access'
                ],
                'restrictions_list': [],
                'is_active': True
            }
        )
        if created:
            self.stdout.write(f'Created VIP Elite membership plan')
        else:
            self.stdout.write(f'VIP Elite membership plan already exists')

        self.stdout.write(
            self.style.SUCCESS('Successfully created/verified all membership plans')
        )
