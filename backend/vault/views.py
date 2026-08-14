from django.db import transaction
from django.db.models import F
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from core.pagination import StandardResultsSetPagination
from vault.models import Resource, ResourceUpvote
from vault.serializers import ResourceUploadSerializer, ResourceSerializer

class ResourceListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    parser_classes = (MultiPartParser, FormParser)
    pagination_class = StandardResultsSetPagination

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ResourceUploadSerializer
        return ResourceSerializer

    def get_queryset(self):
        queryset = Resource.objects.filter(is_active=True).select_related('uploader', 'subject', 'course').order_by('-id')
        
        subject_slug = self.request.query_params.get('subject')
        if subject_slug:
            queryset = queryset.filter(subject__slug=subject_slug)
            
        course_code = self.request.query_params.get('course')
        if course_code:
            queryset = queryset.filter(course__code=course_code)
            
        search_query = self.request.query_params.get('search') or self.request.query_params.get('title')
        if search_query:
            queryset = queryset.filter(title__icontains=search_query)
            
        return queryset

    def create(self, request, *args, **kwargs):
        # Use ResourceUploadSerializer for creation, but return ResourceSerializer representation
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        resource = serializer.save()
        response_serializer = ResourceSerializer(resource, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class ResourceDetailView(generics.RetrieveAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = ResourceSerializer
    queryset = Resource.objects.filter(is_active=True).select_related('uploader', 'subject', 'course')

class UpvoteToggleView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, id):
        try:
            resource = Resource.objects.get(id=id, is_active=True)
        except Resource.DoesNotExist:
            return Response(
                {"code": "not_found", "message": "Resource not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # A user cannot upvote their own resource (403 Forbidden)
        if resource.uploader == request.user:
            return Response(
                {
                    "code": "self_upvote_forbidden",
                    "message": "You cannot upvote your own resource."
                },
                status=status.HTTP_403_FORBIDDEN
            )

        with transaction.atomic():
            upvote_qs = ResourceUpvote.objects.filter(resource=resource, user=request.user)
            if upvote_qs.exists():
                upvote_qs.delete()
                resource.upvote_count = F('upvote_count') - 1
                resource.save(update_fields=['upvote_count'])
                has_upvoted = False
            else:
                ResourceUpvote.objects.create(resource=resource, user=request.user)
                resource.upvote_count = F('upvote_count') + 1
                resource.save(update_fields=['upvote_count'])
                has_upvoted = True

        # Refresh the resource count from DB to return the correct count value
        resource.refresh_from_db()

        return Response({
            "upvote_count": resource.upvote_count,
            "has_upvoted": has_upvoted
        }, status=status.HTTP_200_OK)
