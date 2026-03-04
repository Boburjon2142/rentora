from rest_framework import generics, permissions, viewsets

from .models import AgentProfile
from .serializers import RegisterSerializer, UserSerializer, AgentProfileSerializer


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [permissions.AllowAny]


class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user


class AgentProfileViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = AgentProfile.objects.select_related('user').all()
    serializer_class = AgentProfileSerializer
