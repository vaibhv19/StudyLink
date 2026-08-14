from django.urls import path
from vault.views import ResourceListCreateView, ResourceDetailView

urlpatterns = [
    path('', ResourceListCreateView.as_view(), name='resource-list-create'),
    path('<uuid:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
]
