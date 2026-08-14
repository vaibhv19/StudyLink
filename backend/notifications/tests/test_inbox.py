import uuid
from django.contrib.auth import get_user_model
from rest_framework import status
from rest_framework.test import APITestCase
from notifications.models import Notification

User = get_user_model()


class NotificationInboxAPITests(APITestCase):
    def setUp(self):
        self.user1 = User.objects.create_user(
            email='alice@example.com',
            password='password123',
            full_name='Alice Smith'
        )
        self.user2 = User.objects.create_user(
            email='bob@example.com',
            password='password123',
            full_name='Bob Jones'
        )

        # Create notifications for user1
        self.notif1 = Notification.objects.create(
            recipient=self.user1,
            type=Notification.NotificationType.NEW_REQUEST,
            title='First Alert',
            message='You have a new request.',
            is_read=False
        )
        self.notif2 = Notification.objects.create(
            recipient=self.user1,
            type=Notification.NotificationType.REQUEST_ACCEPTED,
            title='Second Alert',
            message='Your request was accepted.',
            is_read=False
        )

        # Create notification for user2
        self.notif_user2 = Notification.objects.create(
            recipient=self.user2,
            type=Notification.NotificationType.UPVOTE_RECEIVED,
            title='Bob Alert',
            message='Upvote on Bob resource.',
            is_read=False
        )

        self.inbox_url = '/api/v1/notifications/'

    def test_anonymous_inbox_access_rejected(self):
        response = self.client.get(self.inbox_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_sees_only_own_notifications(self):
        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.inbox_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 2)

        # Verify items belong only to user1 and are sorted newest first
        results = response.data['results']
        result_ids = [item['id'] for item in results]
        self.assertIn(str(self.notif2.id), result_ids)
        self.assertIn(str(self.notif1.id), result_ids)
        self.assertNotIn(str(self.notif_user2.id), result_ids)
        self.assertEqual(results[0]['id'], str(self.notif2.id))

    def test_inbox_pagination(self):
        # Create additional 22 notifications for user1 to total 24
        for i in range(22):
            Notification.objects.create(
                recipient=self.user1,
                type=Notification.NotificationType.NEW_COMMENT,
                title=f'Comment Alert {i}',
                message=f'Message {i}'
            )

        self.client.force_authenticate(user=self.user1)
        response = self.client.get(self.inbox_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['count'], 24)
        self.assertEqual(len(response.data['results']), 20)
        self.assertIsNotNone(response.data['next'])

        # Page 2
        page2_response = self.client.get(response.data['next'])
        self.assertEqual(page2_response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(page2_response.data['results']), 4)

    def test_mark_single_notification_as_read(self):
        self.client.force_authenticate(user=self.user1)
        read_url = f'/api/v1/notifications/{self.notif1.id}/read/'
        response = self.client.patch(read_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_read'])

        self.notif1.refresh_from_db()
        self.assertTrue(self.notif1.is_read)

    def test_mark_single_notification_user_isolation(self):
        # User 1 attempting to mark User 2's notification as read should return 404
        self.client.force_authenticate(user=self.user1)
        read_url = f'/api/v1/notifications/{self.notif_user2.id}/read/'
        response = self.client.patch(read_url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.notif_user2.refresh_from_db()
        self.assertFalse(self.notif_user2.is_read)

    def test_mark_single_nonexistent_notification_returns_404(self):
        self.client.force_authenticate(user=self.user1)
        random_id = uuid.uuid4()
        read_url = f'/api/v1/notifications/{random_id}/read/'
        response = self.client.patch(read_url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)

    def test_mark_all_notifications_as_read(self):
        self.client.force_authenticate(user=self.user1)
        mark_all_url = '/api/v1/notifications/mark-all-read/'
        response = self.client.post(mark_all_url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['updated_count'], 2)

        self.notif1.refresh_from_db()
        self.notif2.refresh_from_db()
        self.notif_user2.refresh_from_db()

        self.assertTrue(self.notif1.is_read)
        self.assertTrue(self.notif2.is_read)
        # User 2's notification must remain unread
        self.assertFalse(self.notif_user2.is_read)

    def test_anonymous_mark_read_rejected(self):
        read_url = f'/api/v1/notifications/{self.notif1.id}/read/'
        response = self.client.patch(read_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

        mark_all_url = '/api/v1/notifications/mark-all-read/'
        response = self.client.post(mark_all_url)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
