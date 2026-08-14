from rest_framework import generics, permissions, status
from rest_framework.parsers import MultiPartParser, FormParser
from rest_framework.response import Response
from django.db.models import Subquery, OuterRef
from django.utils import timezone
from datetime import timedelta
from market.models import Listing, ListingStatusHistory
from market.serializers import ListingSerializer, ListingCreateSerializer

from rest_framework.views import APIView
from rest_framework.exceptions import ValidationError
from django.db import transaction, IntegrityError
from market.models import Listing, ListingRequest, ListingStatusHistory
from market.serializers import ListingSerializer, ListingCreateSerializer, ListingRequestSerializer
from notifications.tasks import send_notification_task

class ListingListCreateView(generics.ListCreateAPIView):
    parser_classes = (MultiPartParser, FormParser)

    def get_serializer_class(self):
        if self.request.method == 'POST':
            return ListingCreateSerializer
        return ListingSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [permissions.IsAuthenticated()]
        return [permissions.AllowAny()]

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

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        listing = serializer.save()
        response_serializer = ListingSerializer(listing, context=self.get_serializer_context())
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

class ListingDetailView(generics.RetrieveAPIView):
    queryset = Listing.objects.filter(is_active=True)
    serializer_class = ListingSerializer
    permission_classes = [permissions.AllowAny]
    lookup_field = 'id'
    lookup_url_kwarg = 'id'

class RequestItemView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        try:
            listing = Listing.objects.get(id=id, is_active=True)
        except Listing.DoesNotExist:
            return Response(
                {"code": "not_found", "message": "Listing not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        # 1. Requester cannot be the listing owner
        if listing.owner == request.user:
            raise ValidationError("You cannot request your own listing.")

        # 2. Listing must be AVAILABLE
        if listing.status != 'AVAILABLE':
            raise ValidationError("This listing is no longer available.")

        # 3. Duplicate request is rejected
        if ListingRequest.objects.filter(listing=listing, requester=request.user).exists():
            raise ValidationError("You have already requested this item.")

        try:
            listing_request = ListingRequest.objects.create(
                listing=listing,
                requester=request.user,
                status='PENDING'
            )
        except IntegrityError:
            raise ValidationError("You have already requested this item.")

        owner_id = str(listing.owner_id)
        user_name = request.user.full_name or request.user.email
        listing_title = listing.title
        transaction.on_commit(lambda: send_notification_task.delay(
            owner_id,
            'NEW_REQUEST',
            f"New request for {listing_title}",
            f"{user_name} has requested your item: {listing_title}."
        ))

        serializer = ListingRequestSerializer(listing_request, context={'request': request})
        return Response(serializer.data, status=status.HTTP_201_CREATED)

class AcceptRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        return self._handle_accept(request, id)

    def patch(self, request, id):
        return self._handle_accept(request, id)

    def _handle_accept(self, request, id):
        from market.services import accept_request
        request_obj = accept_request(request.user, id)
        serializer = ListingRequestSerializer(request_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CancelRequestView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        return self._handle_cancel(request, id)

    def patch(self, request, id):
        return self._handle_cancel(request, id)

    def _handle_cancel(self, request, id):
        from market.services import cancel_request
        request_obj = cancel_request(request.user, id)
        serializer = ListingRequestSerializer(request_obj, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

class CompleteHandoffView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def post(self, request, id):
        return self._handle_complete(request, id)

    def patch(self, request, id):
        return self._handle_complete(request, id)

    def _handle_complete(self, request, id):
        from market.services import complete_handoff
        listing = complete_handoff(request.user, id)
        serializer = ListingSerializer(listing, context={'request': request})
        return Response(serializer.data, status=status.HTTP_200_OK)

from rest_framework.exceptions import NotFound, PermissionDenied
from market.serializers import ListingStatusHistorySerializer

class ListingHistoryView(generics.ListAPIView):
    serializer_class = ListingStatusHistorySerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        listing_id = self.kwargs.get('id')
        try:
            listing = Listing.objects.get(id=listing_id, is_active=True)
        except Listing.DoesNotExist:
            raise NotFound("Listing not found.")

        # Enforce that only the listing owner can view history
        if listing.owner != self.request.user:
            raise PermissionDenied("You do not have permission to view the history of this listing.")

        return ListingStatusHistory.objects.filter(listing=listing).select_related('changed_by').order_by('changed_at')

class OwnerDashboardView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        # Fetch user's listings, prefetching requests and their requesters to avoid N+1 queries
        listings = Listing.objects.filter(owner=request.user, is_active=True).prefetch_related('requests__requester').order_by('-id')
        
        my_listings_data = []
        for l in listings:
            reqs = l.requests.all().order_by('-created_at')
            recent_reqs_data = []
            for r in reqs:
                recent_reqs_data.append({
                    "id": str(r.id),
                    "user_name": r.requester.full_name,
                    "created_at": r.created_at.isoformat()
                })
            
            my_listings_data.append({
                "id": str(l.id),
                "title": l.title,
                "status": l.status,
                "request_count": reqs.count(),
                "recent_requests": recent_reqs_data
            })

        # Fetch requests sent by the active user to other listings
        active_requests = ListingRequest.objects.filter(requester=request.user).select_related('listing').order_by('-created_at')
        my_active_requests_data = []
        for ar in active_requests:
            my_active_requests_data.append({
                "listing_id": str(ar.listing.id),
                "listing_title": ar.listing.title,
                "status": ar.status
            })

        return Response({
            "my_listings": my_listings_data,
            "my_active_requests": my_active_requests_data
        }, status=status.HTTP_200_OK)


