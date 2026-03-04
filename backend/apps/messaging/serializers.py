from rest_framework import serializers

from .models import Conversation, Message
from apps.users.models import User
from apps.users.serializers import UserSerializer


class MessageSerializer(serializers.ModelSerializer):
    sender = UserSerializer(read_only=True)

    class Meta:
        model = Message
        fields = ('id', 'conversation', 'sender', 'content', 'is_read', 'created_at')
        read_only_fields = ('sender', 'is_read', 'created_at')


class ConversationSerializer(serializers.ModelSerializer):
    participants = UserSerializer(many=True, read_only=True)
    messages = MessageSerializer(many=True, read_only=True)
    participant_ids = serializers.PrimaryKeyRelatedField(
        queryset=User.objects.all(), many=True, write_only=True, required=False
    )

    class Meta:
        model = Conversation
        fields = ('id', 'participants', 'participant_ids', 'property', 'created_at', 'messages')

    def create(self, validated_data):
        participants = validated_data.pop('participant_ids', [])
        conversation = Conversation.objects.create(**validated_data)
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            conversation.participants.add(request.user)
        if participants:
            conversation.participants.add(*participants)
        return conversation
