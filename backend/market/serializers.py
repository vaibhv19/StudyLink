from rest_framework import serializers
from core.serializers import SubjectSerializer, CourseSerializer
from accounts.serializers import UserDetailSerializer
from market.models import Listing

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
