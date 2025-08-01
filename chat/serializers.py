from rest_framework import serializers
from .models import Message

class MessageSerializer(serializers.ModelSerializer):
    class Meta:
        model = Message
        fields = ['id', 'user', 'text', 'response', 'created_at']
        read_only_fields = ('response', 'created_at', 'user')
