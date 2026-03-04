from rest_framework import viewsets, permissions

from .models import Conversation, Message
from .serializers import ConversationSerializer, MessageSerializer


class IsConversationParticipant(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if isinstance(obj, Conversation):
            return obj.participants.filter(id=request.user.id).exists()
        return obj.conversation.participants.filter(id=request.user.id).exists()


class ConversationViewSet(viewsets.ModelViewSet):
    serializer_class = ConversationSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        return Conversation.objects.filter(participants=self.request.user).prefetch_related('participants', 'messages')

    def perform_create(self, serializer):
        serializer.save()


class MessageViewSet(viewsets.ModelViewSet):
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated, IsConversationParticipant]

    def get_queryset(self):
        return Message.objects.filter(conversation__participants=self.request.user).select_related('sender', 'conversation')

    def perform_create(self, serializer):
        serializer.save(sender=self.request.user)
