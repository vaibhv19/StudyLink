from django.urls import path
from vault.views import ResourceListCreateView, ResourceDetailView, UpvoteToggleView

urlpatterns = [
    path('', ResourceListCreateView.as_view(), name='resource-list-create'),
    path('<uuid:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
    path('<uuid:id>/rate/', UpvoteToggleView.as_view(), name='resource-upvote-toggle'),
]
