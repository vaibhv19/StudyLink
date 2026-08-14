from rest_framework import generics, permissions
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
