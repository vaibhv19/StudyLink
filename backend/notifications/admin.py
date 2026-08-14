from django.contrib import admin
from notifications.models import Notification


@admin.register(Notification)
class NotificationAdmin(admin.ModelAdmin):
    list_display = ('id', 'recipient', 'type', 'title', 'is_read', 'created_at')
    list_filter = ('type', 'is_read', 'created_at')
    search_fields = ('title', 'message', 'recipient__email')
    ordering = ('-created_at',)
