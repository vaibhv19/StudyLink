from django.urls import path
from vault.views import ResourceListCreateView

urlpatterns = [
    path('', ResourceListCreateView.as_view(), name='resource-list-create'),
]
