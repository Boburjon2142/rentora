from django.contrib import admin
from .models import Property, PropertyImage, Favorite


class PropertyImageInline(admin.TabularInline):
    model = PropertyImage
    extra = 1


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ('id', 'title', 'city', 'price', 'property_type', 'is_premium', 'is_active')
    list_filter = ('property_type', 'is_premium', 'is_active', 'city')
    search_fields = ('title', 'city', 'address')
    inlines = [PropertyImageInline]


admin.site.register(Favorite)
