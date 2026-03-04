from django.db import models
from django.conf import settings


class PropertyType(models.TextChoices):
    APARTMENT_RENT = 'apartment_rent', 'Apartment Rent'
    HOUSE_RENT = 'house_rent', 'House Rent'
    PROPERTY_SALE = 'property_sale', 'Property Sale'
    COMMERCIAL = 'commercial', 'Commercial'
    DAILY_RENT = 'daily_rent', 'Daily Rent'
    NEW_CONSTRUCTION = 'new_construction', 'New Construction'


class QarshiDistrict(models.TextChoices):
    MITTI_1 = 'qarshi_1_mitti', 'Qarshi 1-mitti tuman'
    MITTI_2 = 'qarshi_2_mitti', 'Qarshi 2-mitti tuman'
    MITTI_3 = 'qarshi_3_mitti', 'Qarshi 3-mitti tuman'
    MITTI_4 = 'qarshi_4_mitti', 'Qarshi 4-mitti tuman'
    MITTI_5 = 'qarshi_5_mitti', 'Qarshi 5-mitti tuman'
    MITTI_6 = 'qarshi_6_mitti', 'Qarshi 6-mitti tuman'
    MITTI_7 = 'qarshi_7_mitti', 'Qarshi 7-mitti tuman'


class Property(models.Model):
    owner = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='properties')
    title = models.CharField(max_length=180)
    description = models.TextField()
    property_type = models.CharField(max_length=32, choices=PropertyType.choices, db_index=True)
    city = models.CharField(max_length=100, db_index=True)
    district = models.CharField(max_length=32, choices=QarshiDistrict.choices, blank=True, db_index=True)
    address = models.CharField(max_length=255)
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    price = models.DecimalField(max_digits=12, decimal_places=2, db_index=True)
    bedrooms = models.PositiveSmallIntegerField(default=0)
    bathrooms = models.PositiveSmallIntegerField(default=0)
    area_m2 = models.PositiveIntegerField(default=0, db_index=True)
    is_premium = models.BooleanField(default=False, db_index=True)
    is_active = models.BooleanField(default=True, db_index=True)
    view_count = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True, db_index=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        indexes = [
            models.Index(fields=['city', 'property_type']),
            models.Index(fields=['price', 'created_at']),
        ]
        ordering = ['-is_premium', '-created_at']

    def __str__(self):
        return self.title

    def get_absolute_url(self):
        from django.urls import reverse
        return reverse('website:property_detail', args=[self.pk])


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/%Y/%m/')
    is_primary = models.BooleanField(default=False)


class Favorite(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='favorites')
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='favorited_by')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'property')
        indexes = [models.Index(fields=['user', 'created_at'])]
