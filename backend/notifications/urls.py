from django.urls import path
from notifications.views import (
    NotificationInboxView,
    NotificationMarkReadView,
    NotificationMarkAllReadView,
)

urlpatterns = [
    path('', NotificationInboxView.as_view(), name='notification-inbox'),
    path('<uuid:id>/read/', NotificationMarkReadView.as_view(), name='notification-mark-read'),
    path('mark-all-read/', NotificationMarkAllReadView.as_view(), name='notification-mark-all-read'),
]

