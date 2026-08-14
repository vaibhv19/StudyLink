from rest_framework import serializers
from core.models import Subject, Course
from core.serializers import SubjectSerializer, CourseSerializer
from accounts.serializers import UserDetailSerializer
from market.models import Listing, ListingRequest

class ListingSerializer(serializers.ModelSerializer):
    owner = UserDetailSerializer(read_only=True)
    subject = SubjectSerializer(read_only=True)
    course = CourseSerializer(read_only=True)
    photo_url = serializers.SerializerMethodField()
    has_requested = serializers.SerializerMethodField()

    class Meta:
        model = Listing
        fields = (
            'id', 'owner', 'title', 'status', 'photo_url', 'pickup_area',
            'condition', 'is_active', 'subject', 'course', 'has_requested'
        )
        read_only_fields = fields

    def get_photo_url(self, obj):
        if not obj.photo_url:
            return None
        request = self.context.get('request')
        if request is not None:
            return request.build_absolute_uri(obj.photo_url.url)
        return obj.photo_url.url

    def get_has_requested(self, obj):
        request = self.context.get('request')
        if request and request.user and request.user.is_authenticated:
            return obj.requests.filter(requester=request.user).exists()
        return False

class ListingCreateSerializer(serializers.ModelSerializer):
    photo = serializers.FileField(write_only=True)
    subject = serializers.PrimaryKeyRelatedField(queryset=Subject.objects.all(), required=False, allow_null=True)
    course = serializers.PrimaryKeyRelatedField(queryset=Course.objects.all(), required=False, allow_null=True)

    class Meta:
        model = Listing
        fields = ('id', 'title', 'photo', 'pickup_area', 'condition', 'subject', 'course', 'status', 'is_active')
        read_only_fields = ('id', 'status', 'is_active')

    def validate(self, data):
        subject = data.get('subject')
        course = data.get('course')
        if course and subject and course.subject != subject:
            raise serializers.ValidationError({"course": "The course must belong to the selected subject."})
        return data

    def create(self, validated_data):
        photo = validated_data.pop('photo')
        validated_data['photo_url'] = photo
        validated_data['status'] = 'AVAILABLE'
        validated_data['is_active'] = True
        validated_data['owner'] = self.context['request'].user
        return super().create(validated_data)

class ListingRequestSerializer(serializers.ModelSerializer):
    requester = UserDetailSerializer(read_only=True)

    class Meta:
        model = ListingRequest
        fields = ('id', 'listing', 'requester', 'status', 'created_at')
        read_only_fields = ('id', 'listing', 'requester', 'status', 'created_at')

from market.models import ListingStatusHistory

class ListingStatusHistorySerializer(serializers.ModelSerializer):
    changed_by = UserDetailSerializer(read_only=True)

    class Meta:
        model = ListingStatusHistory
        fields = ('id', 'listing', 'from_status', 'to_status', 'changed_by', 'reason', 'changed_at')
        read_only_fields = fields

