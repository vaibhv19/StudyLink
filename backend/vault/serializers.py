import os
from rest_framework import serializers
from django.contrib.auth import get_user_model
from core.models import Subject, Course
from core.serializers import SubjectSerializer, CourseSerializer
from accounts.serializers import UserDetailSerializer
from vault.models import Resource

User = get_user_model()

class ResourceSerializer(serializers.ModelSerializer):
    uploader = UserDetailSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    file_path = serializers.SerializerMethodField()
    has_upvoted = serializers.SerializerMethodField()

    class Meta:
        model = Resource
        fields = (
            'id', 'uploader', 'title', 'file_path', 'subject', 'course',
            'status', 'is_active', 'upvote_count', 'has_upvoted'
        )
        read_only_fields = fields

    def get_file_path(self, obj):
        if not obj.file_path:
            return None
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.file_path.url)
        return obj.file_path.url

    def get_has_upvoted(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.upvotes.filter(user=request.user).exists()
        return False

class ResourceUploadSerializer(serializers.ModelSerializer):
    file = serializers.FileField(write_only=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all())
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all())

    class Meta:
        model = Resource
        fields = ('id', 'title', 'file', 'subject', 'course', 'status', 'upvote_count')
        read_only_fields = ('id', 'status', 'upvote_count')

    def validate_file(self, value):
        ext = os.path.splitext(value.name)[1].lower()
        if ext != '.pdf':
            raise serializers.ValidationError("Only PDF documents are allowed.")
        return value

    def validate(self, data):
        subject = data.get('subject')
        course = data.get('course')
        if course and subject and course.subject != subject:
            raise serializers.ValidationError({"course": "The course must belong to the selected subject."})
        return data

    def create(self, validated_data):
        file = validated_data.pop('file')
        validated_data['file_path'] = file
        validated_data['status'] = 'PROCESSING'
        validated_data['uploader'] = self.context['request'].user
        return super().create(validated_data)
