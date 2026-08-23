from django.db import transaction
from django.db.models import F
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.permissions import IsAuthenticatedOrReadOnly, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from core.pagination import StandardResultsSetPagination
from vault.models import Resource, ResourceUpvote, DoubtBoardComment
from vault.serializers import ResourceUploadSerializer, ResourceSerializer, DoubtBoardCommentSerializer
from notifications.tasks import send_notification_sync

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

        if has_upvoted and resource.uploader != request.user:
            uploader_id = str(resource.uploader_id)
            user_name = request.user.full_name or request.user.email
            resource_title = resource.title
            transaction.on_commit(lambda: send_notification_sync(
                uploader_id,
                'UPVOTE_RECEIVED',
                f"New upvote on {resource_title}",
                f"{user_name} upvoted your study resource '{resource_title}'."
            ))

        return Response({
            "upvote_count": resource.upvote_count,
            "has_upvoted": has_upvoted
        }, status=status.HTTP_200_OK)

class CommentListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAuthenticatedOrReadOnly]
    serializer_class = DoubtBoardCommentSerializer

    def get_queryset(self):
        resource_id = self.kwargs.get('id')
        # Return only top-level comments for this resource. Nested replies are resolved in the serializer.
        return DoubtBoardComment.objects.filter(
            resource_id=resource_id,
            parent=None
        ).select_related('user', 'resource').order_by('created_at')

    def create(self, request, *args, **kwargs):
        resource_id = self.kwargs.get('id')
        try:
            resource = Resource.objects.get(id=resource_id, is_active=True)
        except Resource.DoesNotExist:
            return Response(
                {"code": "not_found", "message": "Resource not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        data = request.data.copy()
        data['resource'] = str(resource.id)

        serializer = self.get_serializer(data=data)
        serializer.is_valid(raise_exception=True)
        comment = serializer.save()

        # Trigger notification to resource uploader
        user_name = request.user.full_name or request.user.email
        resource_title = resource.title
        if resource.uploader != request.user:
            uploader_id = str(resource.uploader_id)
            transaction.on_commit(lambda: send_notification_sync(
                uploader_id,
                'NEW_COMMENT',
                f"New comment on {resource_title}",
                f"{user_name} commented on your study resource '{resource_title}'."
            ))

        # If replying to a parent comment, notify parent comment author
        if comment.parent and comment.parent.user != request.user and comment.parent.user != resource.uploader:
            parent_user_id = str(comment.parent.user_id)
            transaction.on_commit(lambda puid=parent_user_id: send_notification_sync(
                puid,
                'NEW_COMMENT',
                f"New reply on {resource_title}",
                f"{user_name} replied to your comment on '{resource_title}'."
            ))

        return Response(serializer.data, status=status.HTTP_201_CREATED)

class CommentDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def patch(self, request, pk):
        try:
            comment = DoubtBoardComment.objects.select_related('resource').get(pk=pk)
        except DoubtBoardComment.DoesNotExist:
            return Response(
                {"code": "not_found", "message": "Comment not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # Check permissions: must be comment poster or resource uploader
        if request.user != comment.user and request.user != comment.resource.uploader:
            raise PermissionDenied("You do not have permission to modify this comment's solved status.")

        is_solved = request.data.get('is_solved')
        if is_solved is not None:
            comment.is_solved = bool(is_solved)
            comment.save(update_fields=['is_solved'])

        serializer = DoubtBoardCommentSerializer(comment, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)
