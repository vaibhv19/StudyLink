import re
from rest_framework import serializers
from django.contrib.auth import get_user_model

User = get_user_model()

class UserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ('id', 'email', 'full_name', 'avatar_url', 'provider', 'linked_google', 'linked_github')
        read_only_fields = fields

class LoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)

class RegisterSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(validators=[])
    password = serializers.CharField(write_only=True, min_length=8)

    class Meta:
        model = User
        fields = ('email', 'password', 'full_name')

    def validate_email(self, value):
        value = value.lower().strip()
        # Check if email exists
        if User.objects.filter(email=value).exists():
            # We don't raise validation error here directly if we want to handle 409 conflict
            # Wait, standard registration handles validation. If we raise ValidationError, DRF returns 400 Bad Request.
            # But the requirement says:
            # "If the email already exists and is associated with a local provider account, return 400 Bad Request."
            # "If the email exists but has only oauth provider flags set, return 409 Conflict."
            # So in the serializer, we should NOT raise a validation error for email uniqueness if we want to return a 409 Conflict.
            # Instead, we will handle uniqueness and conflict checks in the RegisterView itself!
            # That is a brilliant design decision that allows us to distinguish between 400 and 409!
            pass
        return value

    def validate_password(self, value):
        if not re.search(r'[0-9]', value) and not re.search(r'[^a-zA-Z0-9]', value):
            raise serializers.ValidationError("Password must contain at least one number or special character.")
        return value

    def create(self, validated_data):
        return User.objects.create_user(**validated_data)
