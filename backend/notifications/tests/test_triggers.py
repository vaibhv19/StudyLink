import uuid
from django.contrib.auth import get_user_model
from django.test import TestCase, override_settings
from rest_framework.test import APIClient
from core.models import Subject, Course
from market.models import Listing, ListingRequest
from market.services import accept_request, cancel_request, complete_handoff
from notifications.models import Notification
from notifications.tasks import send_notification_task
from vault.models import Resource, DoubtBoardComment

User = get_user_model()


@override_settings(CELERY_TASK_ALWAYS_EAGER=True)
class NotificationTriggerTests(TestCase):
    def setUp(self):
        self.owner = User.objects.create_user(
            email='owner@example.com',
            password='password123',
            full_name='Owner User'
        )
        self.requester1 = User.objects.create_user(
            email='req1@example.com',
            password='password123',
            full_name='Requester One'
        )
        self.requester2 = User.objects.create_user(
            email='req2@example.com',
            password='password123',
            full_name='Requester Two'
        )

        self.subject = Subject.objects.first() or Subject.objects.create(name='Computer Science', slug='cs')
        self.course = Course.objects.first() or Course.objects.create(subject=self.subject, code='CS101', name='Intro to CS')

        self.listing = Listing.objects.create(
            owner=self.owner,
            title='Data Structures Textbook',
            pickup_area='Campus Library Floor 2',
            condition='GOOD',
            subject=self.subject,
            course=self.course
        )

        self.client = APIClient()

    def test_send_notification_task_direct_execution(self):
        result = send_notification_task.delay(
            str(self.requester1.id),
            'NEW_REQUEST',
            'Test Direct Task',
            'Direct task execution body'
        )
        self.assertIsNotNone(result.result)

        notif = Notification.objects.get(id=result.result)
        self.assertEqual(notif.recipient, self.requester1)
        self.assertEqual(notif.type, 'NEW_REQUEST')
        self.assertEqual(notif.title, 'Test Direct Task')
        self.assertFalse(notif.is_read)

    def test_send_notification_task_nonexistent_user(self):
        fake_id = str(uuid.uuid4())
        result = send_notification_task.delay(
            fake_id,
            'NEW_REQUEST',
            'Invalid User Task',
            'Should abort gracefully'
        )
        self.assertIsNone(result.result)

    def test_marketplace_request_item_triggers_owner_notification(self):
        self.client.force_authenticate(user=self.requester1)
        url = f'/api/v1/market/{self.listing.id}/request/'
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 201)

        # Listing owner must receive NEW_REQUEST alert
        owner_notif = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.NotificationType.NEW_REQUEST
        ).first()
        self.assertIsNotNone(owner_notif)
        self.assertIn(self.listing.title, owner_notif.title)
        self.assertIn(self.requester1.full_name, owner_notif.message)

    def test_marketplace_accept_request_triggers_notifications(self):
        req1 = ListingRequest.objects.create(listing=self.listing, requester=self.requester1)
        req2 = ListingRequest.objects.create(listing=self.listing, requester=self.requester2)

        with self.captureOnCommitCallbacks(execute=True):
            accept_request(self.owner, req1.id)

        # 1. Selected recipient receives REQUEST_ACCEPTED with pickup area details
        notif_accepted = Notification.objects.filter(
            recipient=self.requester1,
            type=Notification.NotificationType.REQUEST_ACCEPTED
        ).first()
        self.assertIsNotNone(notif_accepted)
        self.assertIn(self.listing.title, notif_accepted.title)
        self.assertIn(self.listing.pickup_area, notif_accepted.message)

        # 2. Other active requester receives ITEM_CLAIMED notification
        notif_rejected = Notification.objects.filter(
            recipient=self.requester2,
            type=Notification.NotificationType.ITEM_CLAIMED
        ).first()
        self.assertIsNotNone(notif_rejected)
        self.assertIn(self.listing.title, notif_rejected.title)
        self.assertIn("no longer available", notif_rejected.message)

    def test_marketplace_cancel_by_owner_triggers_requester_notification(self):
        req1 = ListingRequest.objects.create(listing=self.listing, requester=self.requester1)
        with self.captureOnCommitCallbacks(execute=True):
            cancel_request(self.owner, req1.id)

        notif_declined = Notification.objects.filter(
            recipient=self.requester1,
            type=Notification.NotificationType.REQUEST_CANCELED
        ).first()
        self.assertIsNotNone(notif_declined)
        self.assertIn("declined", notif_declined.title.lower())

    def test_marketplace_cancel_by_accepted_requester_triggers_owner_notification(self):
        req1 = ListingRequest.objects.create(listing=self.listing, requester=self.requester1)
        with self.captureOnCommitCallbacks(execute=True):
            accept_request(self.owner, req1.id)

        # Requester withdraws their accepted request
        with self.captureOnCommitCallbacks(execute=True):
            cancel_request(self.requester1, req1.id)

        notif_withdrawn = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.NotificationType.REQUEST_CANCELED
        ).first()
        self.assertIsNotNone(notif_withdrawn)
        self.assertIn("withdrawn", notif_withdrawn.title.lower())

    def test_marketplace_complete_handoff_triggers_item_claimed_notification(self):
        req1 = ListingRequest.objects.create(listing=self.listing, requester=self.requester1)
        with self.captureOnCommitCallbacks(execute=True):
            accept_request(self.owner, req1.id)

        with self.captureOnCommitCallbacks(execute=True):
            complete_handoff(self.owner, self.listing.id)

        notif_handoff = Notification.objects.filter(
            recipient=self.requester1,
            type=Notification.NotificationType.ITEM_CLAIMED
        ).first()
        self.assertIsNotNone(notif_handoff)
        self.assertIn("handoff", notif_handoff.title.lower())

    def test_vault_upvote_triggers_uploader_notification(self):
        resource = Resource.objects.create(
            uploader=self.owner,
            title='Physics Formula Sheet',
            file_path='physics.pdf',
            subject=self.subject,
            course=self.course
        )

        self.client.force_authenticate(user=self.requester1)
        url = f'/api/v1/vault/{resource.id}/rate/'
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url)
        self.assertEqual(response.status_code, 200)

        notif_upvote = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.NotificationType.UPVOTE_RECEIVED
        ).first()
        self.assertIsNotNone(notif_upvote)
        self.assertIn(resource.title, notif_upvote.title)

    def test_vault_comment_triggers_uploader_notification(self):
        resource = Resource.objects.create(
            uploader=self.owner,
            title='Calculus Practice Exam',
            file_path='calc.pdf',
            subject=self.subject,
            course=self.course
        )

        self.client.force_authenticate(user=self.requester1)
        url = f'/api/v1/vault/{resource.id}/comments/'
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, {'content': 'How was question 3 solved?'}, format='json')
        self.assertEqual(response.status_code, 201)

        notif_comment = Notification.objects.filter(
            recipient=self.owner,
            type=Notification.NotificationType.NEW_COMMENT
        ).first()
        self.assertIsNotNone(notif_comment)
        self.assertIn(resource.title, notif_comment.title)

    def test_vault_comment_reply_triggers_parent_commenter_notification(self):
        resource = Resource.objects.create(
            uploader=self.owner,
            title='Chemistry Lab Notes',
            file_path='chem.pdf',
            subject=self.subject,
            course=self.course
        )
        parent_comment = DoubtBoardComment.objects.create(
            resource=resource,
            user=self.requester1,
            content='What is the reaction catalyst?'
        )

        # Requester 2 replies to Requester 1's comment
        self.client.force_authenticate(user=self.requester2)
        url = f'/api/v1/vault/{resource.id}/comments/'
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(
                url,
                {'content': 'It is Platinum.', 'parent': str(parent_comment.id)},
                format='json'
            )
        self.assertEqual(response.status_code, 201)

        # Requester 1 (parent author) must receive notification
        notif_reply = Notification.objects.filter(
            recipient=self.requester1,
            type=Notification.NotificationType.NEW_COMMENT
        ).first()
        self.assertIsNotNone(notif_reply)
        self.assertIn("reply", notif_reply.title.lower())

    def test_vault_self_comment_does_not_notify_uploader(self):
        resource = Resource.objects.create(
            uploader=self.owner,
            title='Biology Summary',
            file_path='bio.pdf',
            subject=self.subject,
            course=self.course
        )

        # Owner comments on their own resource
        self.client.force_authenticate(user=self.owner)
        url = f'/api/v1/vault/{resource.id}/comments/'
        with self.captureOnCommitCallbacks(execute=True):
            response = self.client.post(url, {'content': 'Updated section 2.'}, format='json')
        self.assertEqual(response.status_code, 201)

        owner_notif_count = Notification.objects.filter(recipient=self.owner).count()
        self.assertEqual(owner_notif_count, 0)

