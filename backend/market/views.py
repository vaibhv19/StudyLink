from rest_framework import generics, permissions
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from datetime import timedelta
from market.models import Listing, ListingStatusHistory
from market.serializers import ListingSerializer

class ListingListCreateView(generics.ListAPIView):
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]

    def get_queryset(self):
        # Subquery to find the latest GIVEN_AWAY transition time for each listing
        history_subquery = ListingStatusHistory.objects.filter(
            listing=OuterRef('pk'),
            to_status='GIVEN_AWAY'
        ).order_by('-changed_at').values('changed_at')[:1]

        queryset = Listing.objects.annotate(
            given_away_at=Subquery(history_subquery)
        ).select_related('owner', 'subject', 'course')

        # Filter: only is_active = True
        queryset = queryset.filter(is_active=True)

        # Filter out status = GIVEN_AWAY older than 24 hours
        cutoff = timezone.now() - timedelta(hours=24)
        queryset = queryset.exclude(
            status='GIVEN_AWAY',
            given_away_at__lt=cutoff
        )

        # Filters from query params
        pickup_area = self.request.query_params.get('pickup_area')
        if pickup_area:
            queryset = queryset.filter(pickup_area__icontains=pickup_area)

        subject = self.request.query_params.get('subject')
        if subject:
            queryset = queryset.filter(subject__slug=subject)

        condition = self.request.query_params.get('condition')
        if condition:
            queryset = queryset.filter(condition=condition)

        return queryset.order_by('-id')

class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'
