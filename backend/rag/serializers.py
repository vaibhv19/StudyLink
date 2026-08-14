from rest_framework import serializers
from vault.models import Resource

class ChatQuerySerializer(serializers.Serializer):
    resource_id = serializers.UUIDField(required=True)
    query = serializers.CharField(required=True, allow_blank=False, max_length=1000)

    def validate_resource_id(self, value):
        try:
            resource = Resource.objects.get(id=value, is_active=True)
        except Resource.DoesNotExist:
            raise serializers.ValidationError("Resource not found.")
        
        if resource.status != 'READY':
            raise serializers.ValidationError(
                f"Resource is not ready for chat queries (status: {resource.status})."
            )
        
        return value
