from django.db.models import F
from django_filters import rest_framework as filters
from rest_framework import permissions, viewsets, decorators, response, status

from .models import Property, Favorite, PropertyType
from .serializers import PropertySerializer, FavoriteSerializer


class IsOwnerOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_authenticated

    def has_object_permission(self, request, view, obj):
        if request.method in permissions.SAFE_METHODS:
            return True
        return obj.owner == request.user or request.user.role == 'admin'


class PropertyFilter(filters.FilterSet):
    min_price = filters.NumberFilter(field_name='price', lookup_expr='gte')
    max_price = filters.NumberFilter(field_name='price', lookup_expr='lte')
    min_area = filters.NumberFilter(field_name='area_m2', lookup_expr='gte')
    max_area = filters.NumberFilter(field_name='area_m2', lookup_expr='lte')

    class Meta:
        model = Property
        fields = ['property_type', 'city', 'district', 'bedrooms', 'bathrooms', 'is_premium']


class PropertyViewSet(viewsets.ModelViewSet):
    serializer_class = PropertySerializer
    permission_classes = [IsOwnerOrReadOnly]
    filterset_class = PropertyFilter
    search_fields = ['title', 'description', 'city', 'address']
    ordering_fields = ['price', 'created_at', 'area_m2']

    def get_queryset(self):
        return (
            Property.objects.select_related('owner')
            .prefetch_related('images')
            .filter(is_active=True)
        )

    def perform_create(self, serializer):
        requested_premium = bool(serializer.validated_data.get('is_premium', False))
        can_publish_premium = self.request.user.role in ['agent', 'admin']
        serializer.save(owner=self.request.user, is_premium=requested_premium and can_publish_premium)

    @decorators.action(detail=True, methods=['post'], permission_classes=[permissions.AllowAny])
    def increment_view(self, request, pk=None):
        prop = self.get_object()
        Property.objects.filter(pk=prop.pk).update(view_count=F('view_count') + 1)
        prop.refresh_from_db(fields=['view_count'])
        return response.Response({'view_count': prop.view_count}, status=status.HTTP_200_OK)


class FavoriteViewSet(viewsets.ModelViewSet):
    serializer_class = FavoriteSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Favorite.objects.filter(user=self.request.user).select_related('property')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class PropertyTypeViewSet(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]

    def list(self, request):
        data = [{'key': key, 'label': label} for key, label in PropertyType.choices]
        return response.Response(data)
