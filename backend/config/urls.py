"""
URL configuration for config project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Custom apps endpoints
    path('api/v1/auth/', include('accounts.urls')),
    path('api/v1/core/', include('core.urls')),
    # path('api/v1/vault/', include('vault.urls')),
    # path('api/v1/market/', include('market.urls')),
]
