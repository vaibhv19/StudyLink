from unittest.mock import patch
import requests
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class OAuthAccountLinkingIntegrationTests(APITestCase):
    def setUp(self):
        self.google_url = reverse('accounts:social_google')
        self.github_url = reverse('accounts:social_github')
        self.link_url = reverse('accounts:social_link_confirm')

        self.oauth_code = 'integration-oauth-code-xyz'

        self.google_profile = {
            'email': 'student_integration@example.edu',
            'sub': 'google-uid-8888',
            'name': 'Integration Google User',
            'picture': 'https://example.com/google.png'
        }

        self.github_profile = {
            'email': 'student_integration@example.edu',
            'id': 77777,
            'name': 'Integration GitHub User',
            'avatar_url': 'https://example.com/github.png'
        }

    @patch('requests.post')
    @patch('requests.get')
    def test_complete_oauth_collision_and_password_link_flow(self, mock_get, mock_post):
        """
        End-to-End integration test for OAuth account collision:
        1. Existing local user exists with password.
        2. Google OAuth callback triggers 409 Conflict.
        3. User provides correct local password to link-confirm endpoint.
        4. User is successfully linked and authenticated with JWT session.
        """
        # 1. Existing local account
        local_user = User.objects.create_user(
            email='student_integration@example.edu',
            password='MySecureLocalPassword123!',
            full_name='Local Student User'
        )
        self.assertFalse(local_user.linked_google)

        # 2. Google OAuth attempt with same email
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-auth-token'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_profile

        collision_res = self.client.post(self.google_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(collision_res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(collision_res.data['code'], 'account_collision')
        self.assertEqual(collision_res.data['email'], 'student_integration@example.edu')
        self.assertEqual(collision_res.data['provider'], 'google')

        # 3. Submit wrong password -> rejected 401
        wrong_link_data = {
            'email': 'student_integration@example.edu',
            'password': 'IncorrectPassword!',
            'provider': 'google',
            'code': self.oauth_code
        }
        fail_link_res = self.client.post(self.link_url, wrong_link_data, format='json')
        self.assertEqual(fail_link_res.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(fail_link_res.data['code'], 'invalid_credentials')

        local_user.refresh_from_db()
        self.assertFalse(local_user.linked_google)

        # 4. Submit correct password -> successfully linked 200 OK
        correct_link_data = {
            'email': 'student_integration@example.edu',
            'password': 'MySecureLocalPassword123!',
            'provider': 'google',
            'code': self.oauth_code
        }
        success_link_res = self.client.post(self.link_url, correct_link_data, format='json')
        self.assertEqual(success_link_res.status_code, status.HTTP_200_OK)
        self.assertIn('access', success_link_res.data)
        self.assertEqual(success_link_res.data['user']['email'], 'student_integration@example.edu')

        # Verify DB update
        local_user.refresh_from_db()
        self.assertTrue(local_user.linked_google)

    @patch('requests.post')
    @patch('requests.get')
    def test_github_oauth_collision_and_link_flow(self, mock_get, mock_post):
        """
        Verify GitHub OAuth collision and link confirmation.
        """
        local_user = User.objects.create_user(
            email='student_integration@example.edu',
            password='GitHubLinkPassword123!',
            full_name='GitHub Local User'
        )

        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'gh-auth-token'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.github_profile

        # Collision
        res = self.client.post(self.github_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(res.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(res.data['provider'], 'github')

        # Link Confirm
        link_data = {
            'email': 'student_integration@example.edu',
            'password': 'GitHubLinkPassword123!',
            'provider': 'github',
            'code': self.oauth_code
        }
        link_res = self.client.post(self.link_url, link_data, format='json')
        self.assertEqual(link_res.status_code, status.HTTP_200_OK)

        local_user.refresh_from_db()
        self.assertTrue(local_user.linked_github)
