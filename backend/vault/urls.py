from django.urls import path
from vault.views import ResourceListCreateView, ResourceDetailView, UpvoteToggleView, CommentListCreateView, CommentDetailView

urlpatterns = [
    path('', ResourceListCreateView.as_view(), name='resource-list-create'),
    path('<uuid:pk>/', ResourceDetailView.as_view(), name='resource-detail'),
    path('<uuid:id>/rate/', UpvoteToggleView.as_view(), name='resource-upvote-toggle'),
    path('<uuid:id>/comments/', CommentListCreateView.as_view(), name='comment-list-create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment-detail'),
]
