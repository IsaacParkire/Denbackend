from django.db import models
from django.contrib.auth import get_user_model
from django.core.validators import MinValueValidator, MaxValueValidator
from django.utils import timezone

User = get_user_model()


class ServiceCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    image = models.ImageField(upload_to='service_categories/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name_plural = "Service Categories"

    def __str__(self):
        return self.name


class Therapist(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    specializations = models.ManyToManyField(ServiceCategory, blank=True)
    bio = models.TextField(blank=True)
    experience_years = models.PositiveIntegerField(default=0)
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.00)
    hourly_rate = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    is_available = models.BooleanField(default=True)
    profile_image = models.ImageField(upload_to='therapists/', blank=True, null=True)
    certifications = models.TextField(blank=True, help_text="List of certifications")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.user.get_full_name()} - Therapist"

    @property
    def total_reviews(self):
        return self.servicereview_set.count()


class Service(models.Model):
    DURATION_CHOICES = [
        (30, '30 minutes'),
        (60, '1 hour'),
        (90, '1.5 hours'),
        (120, '2 hours'),
        (180, '3 hours'),
    ]

    name = models.CharField(max_length=200)
    category = models.ForeignKey(ServiceCategory, on_delete=models.CASCADE, related_name='services')
    description = models.TextField()
    short_description = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    duration = models.PositiveIntegerField(choices=DURATION_CHOICES, default=60)
    therapists = models.ManyToManyField(Therapist, blank=True, related_name='services')
    image = models.ImageField(upload_to='services/', blank=True, null=True)
    benefits = models.TextField(blank=True, help_text="List of service benefits")
    preparation_notes = models.TextField(blank=True, help_text="What clients should know before booking")
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    level = models.PositiveIntegerField(blank=True, null=True, help_text="Massage level (1-4) for Her Touch services")
    page = models.CharField(max_length=50, blank=True, null=True, help_text="Source page for this service (e.g. 'her_touch', 'her_strength')")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def average_rating(self):
        reviews = self.servicereview_set.all()
        if reviews:
            return sum([review.rating for review in reviews]) / len(reviews)
        return 0

    @property
    def total_reviews(self):
        return self.servicereview_set.count()


class ServicePackage(models.Model):
    name = models.CharField(max_length=200)
    description = models.TextField()
    services = models.ManyToManyField(Service, through='PackageService')
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_percentage = models.DecimalField(max_digits=5, decimal_places=2, default=0.00)
    validity_days = models.PositiveIntegerField(default=90, help_text="Package validity in days")
    image = models.ImageField(upload_to='packages/', blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

    @property
    def original_price(self):
        total = sum([ps.service.price * ps.quantity for ps in self.packageservice_set.all()])
        return total

    @property
    def savings(self):
        return self.original_price - self.price


class PackageService(models.Model):
    package = models.ForeignKey(ServicePackage, on_delete=models.CASCADE)
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)

    class Meta:
        unique_together = ['package', 'service']

    def __str__(self):
        return f"{self.package.name} - {self.service.name} x{self.quantity}"


class ServiceAddon(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=8, decimal_places=2)
    services = models.ManyToManyField(Service, blank=True, related_name='addons')
    duration_minutes = models.PositiveIntegerField(default=0)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TherapistAvailability(models.Model):
    WEEKDAY_CHOICES = [
        (0, 'Monday'),
        (1, 'Tuesday'),
        (2, 'Wednesday'),
        (3, 'Thursday'),
        (4, 'Friday'),
        (5, 'Saturday'),
        (6, 'Sunday'),
    ]

    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, related_name='availability')
    day_of_week = models.IntegerField(choices=WEEKDAY_CHOICES)
    start_time = models.TimeField()
    end_time = models.TimeField()
    is_active = models.BooleanField(default=True)

    class Meta:
        unique_together = ['therapist', 'day_of_week', 'start_time']

    def __str__(self):
        return f"{self.therapist.user.get_full_name()} - {self.get_day_of_week_display()} {self.start_time}-{self.end_time}"


class ServiceReview(models.Model):
    service = models.ForeignKey(Service, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    therapist = models.ForeignKey(Therapist, on_delete=models.CASCADE, blank=True, null=True)
    rating = models.IntegerField(validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ['service', 'user']

    def __str__(self):
        return f"{self.service.name} - {self.rating}/5 by {self.user.email}"