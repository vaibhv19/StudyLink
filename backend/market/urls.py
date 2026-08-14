from django.urls import path
from market.views import ListingListCreateView, ListingDetailView

urlpatterns = [
    path('', ListingListCreateView.as_view(), name='listing-list-create'),
    path('<uuid:id>/', ListingDetailView.as_view(), name='listing-detail'),
]
