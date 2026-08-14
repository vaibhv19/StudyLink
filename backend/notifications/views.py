from rest_framework import generics, permissions, status
from rest_framework.views import APIView
from rest_framework.response import Response
from django.shortcuts import get_object_or_404
from core.pagination import StandardResultsSetPagination
from notifications.models import Notification
from notifications.serializers import NotificationSerializer


class NotificationInboxView(generics.ListAPIView):
    """
    GET /api/v1/notifications/
    Returns a paginated feed of notifications for the authenticated user,
    ordered by creation date descending.
    """
    permission_classes = [permissions.IsAuthenticated]
    serializer_class = NotificationSerializer
    pagination_class = StandardResultsSetPagination

    def get_queryset(self):
        return Notification.objects.filter(recipient=self.request.user).order_by('-created_at')


class NotificationMarkReadView(APIView):
    """
    PATCH /api/v1/notifications/{id}/read/
    Marks an individual notification owned by the authenticated user as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def patch(self, request, id):
        notification = get_object_or_404(
            Notification,
            id=id,
            recipient=request.user
        )
        if not notification.is_read:
            notification.is_read = True
            notification.save(update_fields=['is_read'])

        serializer = NotificationSerializer(notification)
        return Response(serializer.data, status=status.HTTP_200_OK)


class NotificationMarkAllReadView(APIView):
    """
    POST /api/v1/notifications/mark-all-read/
    Marks all notifications for the authenticated user as read.
    """
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request):
        updated_count = Notification.objects.filter(
            recipient=request.user,
            is_read=False
        ).update(is_read=True)

        return Response({
            "message": "All notifications marked as read.",
            "updated_count": updated_count
        }, status=status.HTTP_200_OK)
