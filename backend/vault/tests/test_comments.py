from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from core.models import Subject, Course
from vault.models import Resource, DoubtBoardComment

User = get_user_model()

class DoubtBoardCommentTests(APITestCase):
    def setUp(self):
        # Create users
        self.uploader = User.objects.create_user(
            email='uploader@example.edu',
            password='StrongPassword123!',
            full_name='Resource Owner'
        )
        self.commenter = User.objects.create_user(
            email='commenter@example.edu',
            password='StrongPassword123!',
            full_name='Comment Poster'
        )
        self.replier = User.objects.create_user(
            email='replier@example.edu',
            password='StrongPassword123!',
            full_name='Reply Poster'
        )
        self.other_user = User.objects.create_user(
            email='other@example.edu',
            password='StrongPassword123!',
            full_name='Other Student'
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
            uploader=self.uploader,
            title='Lecture 1 Notes',
            file_path='lect1.pdf',
            subject=self.subject,
            course=self.course,
            status='READY',
            is_active=True
        )

        self.comments_url = reverse('comment-list-create', kwargs={'id': self.resource.id})

    def test_post_comment_success(self):
        self.client.force_authenticate(user=self.commenter)

        data = {
            'content': 'Is the quicksort runtime always O(n log n)?'
        }
        response = self.client.post(self.comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['content'], 'Is the quicksort runtime always O(n log n)?')
        self.assertFalse(response.data['is_solved'])
        self.assertEqual(response.data['user']['email'], self.commenter.email)

        # Verify db
        self.assertEqual(DoubtBoardComment.objects.count(), 1)
        comment = DoubtBoardComment.objects.first()
        self.assertEqual(comment.resource, self.resource)
        self.assertEqual(comment.user, self.commenter)
        self.assertIsNone(comment.parent)

    def test_post_nested_reply_success(self):
        # Create parent comment
        parent = DoubtBoardComment.objects.create(
            resource=self.resource,
            user=self.commenter,
            content="What is quicksort?"
        )

        self.client.force_authenticate(user=self.replier)

        data = {
            'content': 'It is a divide-and-conquer algorithm.',
            'parent': parent.id
        }
        response = self.client.post(self.comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data['parent'], parent.id)

        # Verify db
        self.assertEqual(DoubtBoardComment.objects.count(), 2)
        reply = DoubtBoardComment.objects.exclude(id=parent.id).first()
        self.assertEqual(reply.parent, parent)
        self.assertEqual(reply.user, self.replier)

    def test_post_reply_mismatch_resource_fails(self):
        # Create another resource
        other_resource = Resource.objects.create(
            uploader=self.uploader,
            title='Math Lecture Notes',
            file_path='math.pdf',
            subject=self.subject,
            course=self.course,
            status='READY',
            is_active=True
        )
        # Create comment on other resource
        other_comment = DoubtBoardComment.objects.create(
            resource=other_resource,
            user=self.commenter,
            content="Math question"
        )

        self.client.force_authenticate(user=self.replier)

        # Try to post reply on self.resource referencing a comment on other_resource
        data = {
            'content': 'Invalid reply',
            'parent': other_comment.id
        }
        response = self.client.post(self.comments_url, data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('parent', response.data['fields'])
        self.assertEqual(response.data['fields']['parent'][0], "Parent comment must belong to the same resource.")

    def test_list_comments_returns_nested_tree(self):
        # Create threaded hierarchy:
        # C1 -> C1_R1
        #    -> C1_R2
        # C2
        c1 = DoubtBoardComment.objects.create(resource=self.resource, user=self.commenter, content="C1")
        c1_r1 = DoubtBoardComment.objects.create(resource=self.resource, user=self.replier, parent=c1, content="C1_R1")
        c1_r2 = DoubtBoardComment.objects.create(resource=self.resource, user=self.uploader, parent=c1, content="C1_R2")
        c2 = DoubtBoardComment.objects.create(resource=self.resource, user=self.commenter, content="C2")

        response = self.client.get(self.comments_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify only root level comments (parent=None) are returned in list
        results = response.data['results']
        self.assertEqual(len(results), 2)
        
        # Verify c1 (first chronologically) has replies
        self.assertEqual(results[0]['content'], "C1")
        self.assertEqual(len(results[0]['replies']), 2)
        self.assertEqual(results[0]['replies'][0]['content'], "C1_R1")
        self.assertEqual(results[0]['replies'][1]['content'], "C1_R2")

        # Verify c2 has no replies
        self.assertEqual(results[1]['content'], "C2")
        self.assertEqual(len(results[1]['replies']), 0)

    def test_comment_solved_toggle_by_commenter_success(self):
        comment = DoubtBoardComment.objects.create(
            resource=self.resource,
            user=self.commenter,
            content="Is this correct?"
        )

        self.client.force_authenticate(user=self.commenter)
        patch_url = reverse('comment-detail', kwargs={'pk': comment.id})

        response = self.client.patch(patch_url, {'is_solved': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_solved'])

        comment.refresh_from_db()
        self.assertTrue(comment.is_solved)

    def test_comment_solved_toggle_by_uploader_success(self):
        comment = DoubtBoardComment.objects.create(
            resource=self.resource,
            user=self.commenter,
            content="Is this correct?"
        )

        # Authenticate resource owner (uploader)
        self.client.force_authenticate(user=self.uploader)
        patch_url = reverse('comment-detail', kwargs={'pk': comment.id})

        response = self.client.patch(patch_url, {'is_solved': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data['is_solved'])

    def test_comment_solved_toggle_unauthorized_fails(self):
        comment = DoubtBoardComment.objects.create(
            resource=self.resource,
            user=self.commenter,
            content="Is this correct?"
        )

        # Authenticate other student (neither poster nor resource owner)
        self.client.force_authenticate(user=self.other_user)
        patch_url = reverse('comment-detail', kwargs={'pk': comment.id})

        response = self.client.patch(patch_url, {'is_solved': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
        self.assertEqual(response.data['code'], 'permission_denied')

        comment.refresh_from_db()
        self.assertFalse(comment.is_solved)
