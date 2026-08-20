"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

from django.conf import settings
from django.conf.urls.static import static
from market.views import OwnerDashboardView

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom apps endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/core/', include('core.urls')),
    path('api/v1/vault/', include('vault.urls')),
    path('api/v1/market/', include('market.urls')),
    path('api/v1/chat/', include('rag.urls')),
    path('api/v1/notifications/', include('notifications.urls')),
    path('api/v1/dashboard/owner/', OwnerDashboardView.as_view(), name='owner-dashboard'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)


