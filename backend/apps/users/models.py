from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        USER = 'user', 'User'
        AGENT = 'agent', 'Agent'
        ADMIN = 'admin', 'Admin'

    role = models.CharField(max_length=20, choices=Role.choices, default=Role.USER, db_index=True)
    phone = models.CharField(max_length=24, blank=True)

    def __str__(self):
        return f'{self.username} ({self.role})'


class AgentProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='agent_profile')
    agency_name = models.CharField(max_length=120)
    license_number = models.CharField(max_length=80, blank=True)
    bio = models.TextField(blank=True)
    is_verified = models.BooleanField(default=False, db_index=True)
    whatsapp = models.CharField(max_length=24, blank=True)

    def __str__(self):
        return self.agency_name


class SubscriptionPlan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    max_active_listings = models.PositiveIntegerField(default=5)
    price_monthly = models.DecimalField(max_digits=10, decimal_places=2)
    featured_boost = models.BooleanField(default=False)

    def __str__(self):
        return self.name
