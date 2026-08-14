from rest_framework import serializers
from notifications.models import Notification


class NotificationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notification
        fields = ('id', 'type', 'title', 'message', 'is_read', 'created_at')
        read_only_fields = ('id', 'type', 'title', 'message', 'is_read', 'created_at')
