from django.contrib.auth.models import AbstractUser, BaseUserManager
from django.db import models
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import timedelta


class UserManager(BaseUserManager):
    def create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError('The Email field must be set')
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')

        return self.create_user(email, password, **extra_fields)


class User(AbstractUser):
    username = None
    email = models.EmailField(_('email address'), unique=True)
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    date_of_birth = models.DateField(blank=True, null=True)
    
    GENDER_CHOICES = [
        ('M', 'Male'),
        ('F', 'Female'),
        ('O', 'Other'),
        ('P', 'Prefer not to say'),
    ]
    gender = models.CharField(max_length=1, choices=GENDER_CHOICES, blank=True, null=True)
    
    # Membership Information
    MEMBERSHIP_CHOICES = [
        ('basic', 'Basic Member'),
        ('premium', 'Premium Member'),
        ('vip', 'VIP Elite Member'),
    ]
    membership_type = models.CharField(
        max_length=10, 
        choices=MEMBERSHIP_CHOICES, 
        default='basic',
        help_text="User's current membership level"
    )
    membership_start_date = models.DateTimeField(blank=True, null=True)
    membership_end_date = models.DateTimeField(blank=True, null=True)
    
    MEMBERSHIP_STATUS_CHOICES = [
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('pending', 'Pending Payment'),
    ]
    membership_status = models.CharField(
        max_length=10,
        choices=MEMBERSHIP_STATUS_CHOICES,
        default='active'
    )
    
    # Address field for easier access
    address = models.TextField(blank=True, null=True)
    
    objects = UserManager()
    
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        verbose_name = _('User')
        verbose_name_plural = _('Users')
    
    def __str__(self):
        return self.email
    
    @property
    def full_name(self):
        return f"{self.first_name} {self.last_name}".strip()
    
    @property
    def is_membership_active(self):
        if self.membership_type == 'basic':
            return True
        return (
            self.membership_status == 'active' and 
            self.membership_end_date and 
            self.membership_end_date > timezone.now()
        )
    
    @property
    def membership_display_name(self):
        return dict(self.MEMBERSHIP_CHOICES).get(self.membership_type, 'Basic Member')
    
    def upgrade_membership(self, new_type, duration_months=1):
        """Upgrade user membership to a new type"""
        self.membership_type = new_type
        self.membership_status = 'active'
        self.membership_start_date = timezone.now()
        self.membership_end_date = timezone.now() + timedelta(days=30 * duration_months)
        self.save()
    
    def cancel_membership(self):
        """Cancel membership (downgrade to basic)"""
        self.membership_type = 'basic'
        self.membership_status = 'cancelled'
        self.save()
        return self.email

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    avatar = models.ImageField(upload_to='avatars/', blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True)
    
    # Address Information
    address_line_1 = models.CharField(max_length=255, blank=True)
    address_line_2 = models.CharField(max_length=255, blank=True)
    city = models.CharField(max_length=100, blank=True)
    state = models.CharField(max_length=100, blank=True)
    postal_code = models.CharField(max_length=20, blank=True)
    country = models.CharField(max_length=100, blank=True, default='Kenya')
    
    # Preferences
    preferred_services = models.CharField(max_length=200, blank=True, help_text="Comma-separated list of preferred services")
    marketing_emails = models.BooleanField(default=True)
    sms_notifications = models.BooleanField(default=True)
    
    # Loyalty Program
    loyalty_points = models.PositiveIntegerField(default=0)
    vip_member = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('User Profile')
        verbose_name_plural = _('User Profiles')
    
    def __str__(self):
        return f"{self.user.email} Profile"


class MembershipPlan(models.Model):
    """Defines the available membership plans and their features"""
    
    PLAN_TYPES = [
        ('basic', 'Basic'),
        ('premium', 'Premium'),
        ('vip', 'VIP Elite'),
    ]
    
    name = models.CharField(max_length=50)
    plan_type = models.CharField(max_length=10, choices=PLAN_TYPES, unique=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    currency = models.CharField(max_length=3, default='KSH')
    duration_months = models.PositiveIntegerField(default=1)
    
    # Features
    her_secrets_access = models.BooleanField(default=False)
    premium_events_access = models.BooleanField(default=False)
    vip_events_access = models.BooleanField(default=False)
    priority_booking = models.BooleanField(default=False)
    premium_gallery_access = models.BooleanField(default=False)
    vip_gallery_access = models.BooleanField(default=False)
    custom_experiences = models.BooleanField(default=False)
    concierge_service = models.BooleanField(default=False)
    private_events = models.BooleanField(default=False)
    
    # Descriptions
    description = models.TextField(blank=True)
    features_list = models.JSONField(default=list, help_text="List of features as JSON array")
    restrictions_list = models.JSONField(default=list, help_text="List of restrictions as JSON array")
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Membership Plan')
        verbose_name_plural = _('Membership Plans')
        ordering = ['price']
    
    def __str__(self):
        return f"{self.name} - {self.currency} {self.price}"


class MembershipHistory(models.Model):
    """Track membership changes and payment history"""
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='membership_history')
    plan = models.ForeignKey(MembershipPlan, on_delete=models.CASCADE)
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    start_date = models.DateTimeField()
    end_date = models.DateTimeField()
    
    # Payment Information
    payment_amount = models.DecimalField(max_digits=10, decimal_places=2)
    payment_method = models.CharField(max_length=50, blank=True)
    payment_reference = models.CharField(max_length=100, blank=True)
    payment_date = models.DateTimeField(blank=True, null=True)
    
    # Auto-renewal
    auto_renew = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = _('Membership History')
        verbose_name_plural = _('Membership Histories')
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.user.email} - {self.plan.name} ({self.status})"
