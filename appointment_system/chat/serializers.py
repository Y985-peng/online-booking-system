from rest_framework import serializers
from .models import Conversation, Message
from django.contrib.auth import get_user_model

User = get_user_model()


class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.SerializerMethodField()

    class Meta:
        model = Message
        fields = ['id', 'sender', 'sender_name', 'content', 'is_read', 'created_at']
        read_only_fields = ['sender', 'is_read']

    def get_sender_name(self, obj):
        return obj.sender.username


class ConversationSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    participant_names = serializers.SerializerMethodField()
    service_name = serializers.SerializerMethodField()
    unread_count = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ['id', 'service', 'service_name', 'participant_names', 'last_message', 'unread_count', 'created_at', 'updated_at']

    def get_last_message(self, obj):
        msg = obj.messages.last()
        if msg:
            return {'content': msg.content[:50], 'sender': msg.sender.username, 'time': msg.created_at.strftime('%m-%d %H:%M')}
        return None

    def get_participant_names(self, obj):
        return [u.username for u in obj.participants.all()]

    def get_service_name(self, obj):
        return obj.service.name if obj.service else None

    def get_unread_count(self, obj):
        user = self.context.get('request').user if self.context.get('request') else None
        if not user:
            return 0
        return obj.messages.filter(is_read=False).exclude(sender=user).count()


class CreateConversationSerializer(serializers.Serializer):
    service_id = serializers.IntegerField(required=False, allow_null=True)
    provider_id = serializers.IntegerField(required=True)
