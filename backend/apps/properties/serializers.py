from rest_framework import serializers

from .models import Property, PropertyImage, Favorite
from apps.users.serializers import UserSerializer


class PropertyImageSerializer(serializers.ModelSerializer):
    def validate_image(self, value):
        max_size_mb = 8
        if value.size > max_size_mb * 1024 * 1024:
            raise serializers.ValidationError(f'Image exceeds {max_size_mb}MB limit.')
        allowed = ('.jpg', '.jpeg', '.png', '.webp')
        lower_name = value.name.lower()
        if not lower_name.endswith(allowed):
            raise serializers.ValidationError('Only jpg, jpeg, png, and webp files are allowed.')
        return value

    class Meta:
        model = PropertyImage
        fields = ('id', 'image', 'is_primary')


class PropertySerializer(serializers.ModelSerializer):
    owner = UserSerializer(read_only=True)
    images = PropertyImageSerializer(many=True, required=False)
    is_favorited = serializers.SerializerMethodField()

    class Meta:
        model = Property
        fields = (
            'id', 'owner', 'title', 'description', 'property_type', 'city', 'district', 'address',
            'latitude', 'longitude', 'price', 'bedrooms', 'bathrooms', 'area_m2',
            'is_premium', 'is_active', 'view_count', 'created_at', 'updated_at',
            'images', 'is_favorited'
        )
        read_only_fields = ('view_count',)

    def get_is_favorited(self, obj):
        request = self.context.get('request')
        if not request or request.user.is_anonymous:
            return False
        return obj.favorited_by.filter(user=request.user).exists()

    def create(self, validated_data):
        images_data = validated_data.pop('images', [])
        prop = Property.objects.create(**validated_data)
        for image_data in images_data:
            PropertyImage.objects.create(property=prop, **image_data)
        return prop

    def update(self, instance, validated_data):
        images_data = validated_data.pop('images', None)
        for attr, value in validated_data.items():
            setattr(instance, attr, value)
        instance.save()
        if images_data is not None:
            instance.images.all().delete()
            for image_data in images_data:
                PropertyImage.objects.create(property=instance, **image_data)
        return instance


class FavoriteSerializer(serializers.ModelSerializer):
    property = PropertySerializer(read_only=True)
    property_id = serializers.PrimaryKeyRelatedField(
        source='property', queryset=Property.objects.filter(is_active=True), write_only=True
    )

    class Meta:
        model = Favorite
        fields = ('id', 'property', 'property_id', 'created_at')
        read_only_fields = ('created_at',)
