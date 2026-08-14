from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Subject, Course
from vault.models import Resource, ResourceUpvote

User = get_user_model()

class ResourceUpvoteTests(APITestCase):
    def setUp(self):
        # Create users
        self.user = User.objects.create_user(
            email='student@example.edu',
            password='StrongPassword123!',
            full_name='Study Linker'
        )
        self.other_user = User.objects.create_user(
            email='other@example.edu',
            password='StrongPassword123!',
            full_name='Other Linker'
        )

        # Create subject and course
        self.subject = Subject.objects.create(name='Computer Science', slug='cs')
        self.course = Course.objects.create(
            subject=self.subject,
            name='Intro to Programming',
            code='CS101'
        )

        # Create active resource
        self.resource = Resource.objects.create(
            uploader=self.user,
            title='Calculus Notes',
            file_path='calc.pdf',
            subject=self.subject,
            course=self.course,
            status='READY',
            is_active=True
        )

        self.rate_url = reverse('resource-upvote-toggle', kwargs={'id': self.resource.id})

    def test_upvote_success(self):
        # Authenticate other_user (not the owner)
        self.client.force_authenticate(user=self.other_user)

        response = self.client.post(self.rate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['upvote_count'], 1)
        self.assertTrue(response.data['has_upvoted'])

        # Verify db records
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.upvote_count, 1)
        self.assertTrue(ResourceUpvote.objects.filter(resource=self.resource, user=self.other_user).exists())

    def test_upvote_toggle_off(self):
        # Set up an existing upvote
        ResourceUpvote.objects.create(resource=self.resource, user=self.other_user)
        self.resource.upvote_count = 1
        self.resource.save()

        self.client.force_authenticate(user=self.other_user)

        # Post again to toggle off
        response = self.client.post(self.rate_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['upvote_count'], 0)
        self.assertFalse(response.data['has_upvoted'])

        # Verify db records
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.upvote_count, 0)
        self.assertFalse(ResourceUpvote.objects.filter(resource=self.resource, user=self.other_user).exists())

    def test_upvote_own_resource_fails(self):
        # Authenticate uploader
        self.client.force_authenticate(user=self.user)

        response = self.client.post(self.rate_url)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'self_upvote_forbidden')

        # Verify no upvote was counted
        self.resource.refresh_from_db()
        self.assertEqual(self.resource.upvote_count, 0)
        self.assertEqual(ResourceUpvote.objects.count(), 0)

    def test_upvote_unauthenticated_fails(self):
        response = self.client.post(self.rate_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_upvote_nonexistent_resource_fails(self):
        self.client.force_authenticate(user=self.other_user)
        import uuid
        invalid_url = reverse('resource-upvote-toggle', kwargs={'id': uuid.uuid4()})
        response = self.client.post(invalid_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
