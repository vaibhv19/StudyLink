from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Subject, Course
from market.models import Listing, ListingRequest, ListingStatusHistory
from django.core.files.uploadedfile import SimpleUploadedFile

User = get_user_model()

class MarketplaceAPITests(APITestCase):
    def setUp(self):
        # Create users
        self.owner = User.objects.create_user(
            email='owner@example.edu',
            password='StrongPassword123!',
            full_name='Item Owner'
        )
        self.buyer = User.objects.create_user(
            email='buyer@example.edu',
            password='StrongPassword123!',
            full_name='Item Buyer'
        )

        # Create Subject and Course
        self.subject = Subject.objects.create(name='Mathematics', slug='math')
        self.course = Course.objects.create(
            subject=self.subject,
            name='Calculus I',
            code='MATH101'
        )

        # Create a mock photo file
        self.mock_photo = SimpleUploadedFile(
            name='book.jpg',
            content=b'dummyimagecontent',
            content_type='image/jpeg'
        )

        # URLs
        self.list_url = reverse('listing-list-create')
        self.dashboard_url = reverse('owner-dashboard')

    def test_create_listing_success(self):
        self.client.force_authenticate(user=self.owner)
        data = {
            'title': 'Calculus Textbook',
            'photo': self.mock_photo,
            'pickup_area': 'Science Library Lobby',
            'condition': 'Used - Good',
            'subject': self.subject.id,
            'course': self.course.id
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Listing.objects.count(), 1)
        listing = Listing.objects.first()
        self.assertEqual(listing.title, 'Calculus Textbook')
        self.assertEqual(listing.status, 'AVAILABLE')
        self.assertTrue(listing.is_active)
        self.assertEqual(listing.owner, self.owner)

    def test_create_listing_invalid_course_subject(self):
        self.client.force_authenticate(user=self.owner)
        other_subject = Subject.objects.create(name='Physics', slug='phys')
        data = {
            'title': 'Calculus Textbook',
            'photo': self.mock_photo,
            'pickup_area': 'Science Library Lobby',
            'condition': 'Used - Good',
            'subject': other_subject.id,  # Mismatched subject
            'course': self.course.id
        }
        response = self.client.post(self.list_url, data, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('course', response.data['fields'])

    def test_list_listings_visibility(self):
        # Create active listing
        Listing.objects.create(
            owner=self.owner,
            title='Calculus Book',
            status='AVAILABLE',
            photo_url='listings/book.jpg',
            pickup_area='Campus',
            condition='Used - Good',
            is_active=True,
            subject=self.subject,
            course=self.course
        )
        # Create inactive listing
        Listing.objects.create(
            owner=self.owner,
            title='Inactive Book',
            status='AVAILABLE',
            photo_url='listings/book.jpg',
            pickup_area='Campus',
            condition='Used - Good',
            is_active=False
        )

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Verify inactive is hidden
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Calculus Book')

    def test_given_away_listings_expiry_rules(self):
        self.client.force_authenticate(user=self.owner)
        
        # 1. Listing given away recently (e.g. 2 hours ago) -> should be visible
        recent_listing = Listing.objects.create(
            owner=self.owner,
            title='Recent Handoff Book',
            status='GIVEN_AWAY',
            photo_url='listings/book.jpg',
            pickup_area='Campus',
            condition='Used - Good',
            is_active=True
        )
        ListingStatusHistory.objects.create(
            listing=recent_listing,
            from_status='REQUESTED',
            to_status='GIVEN_AWAY',
            changed_by=self.owner,
            changed_at=timezone.now() - timedelta(hours=2)
        )
        # Force the auto_now_add changed_at column update for test query
        ListingStatusHistory.objects.filter(listing=recent_listing).update(changed_at=timezone.now() - timedelta(hours=2))

        # 2. Listing given away long ago (e.g. 26 hours ago) -> should be hidden
        old_listing = Listing.objects.create(
            owner=self.owner,
            title='Expired Handoff Book',
            status='GIVEN_AWAY',
            photo_url='listings/book.jpg',
            pickup_area='Campus',
            condition='Used - Good',
            is_active=True
        )
        ListingStatusHistory.objects.create(
            listing=old_listing,
            from_status='REQUESTED',
            to_status='GIVEN_AWAY',
            changed_by=self.owner,
            changed_at=timezone.now() - timedelta(hours=26)
        )
        ListingStatusHistory.objects.filter(listing=old_listing).update(changed_at=timezone.now() - timedelta(hours=26))

        response = self.client.get(self.list_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        # Expired handoff must be hidden, recent handoff remains visible
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Recent Handoff Book')

    def test_marketplace_filtering(self):
        # Create different listings
        Listing.objects.create(
            owner=self.owner,
            title='Calculus Book',
            status='AVAILABLE',
            photo_url='listings/book.jpg',
            pickup_area='North Campus',
            condition='New',
            is_active=True,
            subject=self.subject,
            course=self.course
        )
        Listing.objects.create(
            owner=self.owner,
            title='Chemistry Lab Coat',
            status='AVAILABLE',
            photo_url='listings/coat.jpg',
            pickup_area='South Campus',
            condition='Used - Fair',
            is_active=True
        )

        # Filter by pickup area
        response = self.client.get(self.list_url + '?pickup_area=North')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Calculus Book')

        # Filter by condition
        response = self.client.get(self.list_url + '?condition=Used%20-%20Fair')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Chemistry Lab Coat')

        # Filter by subject slug
        response = self.client.get(self.list_url + '?subject=math')
        self.assertEqual(response.data['count'], 1)
        self.assertEqual(response.data['results'][0]['title'], 'Calculus Book')

    def test_listing_detail_view(self):
        listing = Listing.objects.create(
            owner=self.owner,
            title='Chemistry Lab Coat',
            status='AVAILABLE',
            photo_url='listings/coat.jpg',
            pickup_area='South Campus',
            condition='Used - Fair',
            is_active=True
        )
        detail_url = reverse('listing-detail', kwargs={'id': listing.id})
        response = self.client.get(detail_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['title'], 'Chemistry Lab Coat')
        self.assertEqual(response.data['pickup_area'], 'South Campus')
