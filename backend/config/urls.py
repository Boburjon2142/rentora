from django.contrib import admin
from django.urls import include, path
from django.conf import settings
from django.conf.urls.static import static
from django.http import JsonResponse
from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView, TokenVerifyView

from apps.properties.views import PropertyViewSet, PropertyTypeViewSet, FavoriteViewSet
from apps.messaging.views import ConversationViewSet, MessageViewSet
from apps.users.views import RegisterView, ProfileView, AgentProfileViewSet

router = DefaultRouter()
router.register(r'properties', PropertyViewSet, basename='property')
router.register(r'property-types', PropertyTypeViewSet, basename='property-type')
router.register(r'favorites', FavoriteViewSet, basename='favorite')
router.register(r'conversations', ConversationViewSet, basename='conversation')
router.register(r'messages', MessageViewSet, basename='message')
router.register(r'agents', AgentProfileViewSet, basename='agent')

urlpatterns = [
    path('admin/', admin.site.urls),
    path('health/', lambda request: JsonResponse({'status': 'ok'}), name='health'),
    path('', include('apps.website.urls')),
    path('api/v1/auth/register/', RegisterView.as_view(), name='register'),
    path('api/v1/auth/profile/', ProfileView.as_view(), name='profile'),
    path('api/v1/auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/v1/auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('api/v1/auth/token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('api/v1/', include(router.urls)),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
