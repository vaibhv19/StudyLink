from django.urls import path
from market.views import (
    ListingListCreateView, ListingDetailView, RequestItemView,
    AcceptRequestView, CancelRequestView, CompleteHandoffView, ListingHistoryView
)

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list-create'),
    path('<uuid:id>/', ListingDetailView.as_view(), name='listing-detail'),
    path('<uuid:id>/request/', RequestItemView.as_view(), name='request-item'),
    path('requests/<uuid:id>/accept/', AcceptRequestView.as_view(), name='request-accept'),
    path('requests/<uuid:id>/cancel/', CancelRequestView.as_view(), name='request-cancel'),
    path('<uuid:id>/complete/', CompleteHandoffView.as_view(), name='listing-complete'),
    path('<uuid:id>/history/', ListingHistoryView.as_view(), name='listing-history'),
]


