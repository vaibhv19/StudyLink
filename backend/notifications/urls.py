from django.urls import path
from notifications.views import NotificationInboxView

urlpatterns = [
    path('', NotificationInboxView.as_view(), name='notification-inbox'),
]
