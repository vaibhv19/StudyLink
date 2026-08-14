from unittest.mock import patch
import requests
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class OAuthTests(APITestCase):
    def setUp(self):
        self.google_url = reverse('accounts:social_google')
        self.github_url = reverse('accounts:social_github')
        self.link_url = reverse('accounts:social_link_confirm')
        
        self.oauth_code = 'valid-oauth-code-1234'
        self.google_profile = {
            'email': 'student@example.edu',
            'sub': 'google-id-123',
            'name': 'Google Student',
            'picture': 'http://example.com/avatar.jpg'
        }
        self.github_profile = {
            'email': 'student@example.edu',
            'id': 998877,
            'name': 'GitHub Student',
            'avatar_url': 'http://example.com/github.jpg'
        }

    @patch('requests.post')
    @patch('requests.get')
    def test_google_oauth_signup_success(self, mock_get, mock_post):
        # Mock token exchange response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-access-token'}
        # Mock userinfo response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_profile
        
        response = self.client.post(self.google_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Verify user is created correctly
        user = User.objects.get(email='student@example.edu')
        self.assertEqual(user.provider, 'google')
        self.assertTrue(user.linked_google)
        self.assertFalse(user.linked_github)
        self.assertFalse(user.has_usable_password())

    @patch('requests.post')
    @patch('requests.get')
    def test_github_oauth_signup_success(self, mock_get, mock_post):
        # Mock token exchange response
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'github-access-token'}
        # Mock user response
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.github_profile
        
        response = self.client.post(self.github_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        
        # Verify user is created correctly
        user = User.objects.get(email='student@example.edu')
        self.assertEqual(user.provider, 'github')
        self.assertTrue(user.linked_github)

    @patch('requests.post')
    def test_oauth_token_exchange_failure(self, mock_post):
        # Mock token exchange failure
        mock_post.return_value.status_code = 400
        response = self.client.post(self.google_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'oauth_verification_failed')

    @patch('requests.post')
    def test_oauth_provider_timeout(self, mock_post):
        # Mock connection timeout
        mock_post.side_effect = requests.exceptions.Timeout("Timeout!")
        response = self.client.post(self.google_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertIn("timeout", response.data['message'])

    @patch('requests.post')
    @patch('requests.get')
    def test_oauth_login_existing_local_collision(self, mock_get, mock_post):
        # Create existing local account
        User.objects.create_user(
            email='student@example.edu',
            password='LocalPassword123!',
            full_name='Local Student'
        )
        
        # Mock social authentication returning same email
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-access-token'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_profile
        
        response = self.client.post(self.google_url, {'code': self.oauth_code}, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'account_collision')
        self.assertEqual(response.data['provider'], 'google')

    @patch('requests.post')
    @patch('requests.get')
    def test_account_linking_success(self, mock_get, mock_post):
        # Create existing local account
        User.objects.create_user(
            email='student@example.edu',
            password='LocalPassword123!',
            full_name='Local Student'
        )
        
        # Mock social profile details
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-access-token'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_profile
        
        link_data = {
            'email': 'student@example.edu',
            'password': 'LocalPassword123!',
            'provider': 'google',
            'code': self.oauth_code
        }
        response = self.client.post(self.link_url, link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        
        # Verify user is updated
        user = User.objects.get(email='student@example.edu')
        self.assertTrue(user.linked_google)

    @patch('requests.post')
    @patch('requests.get')
    def test_account_linking_invalid_password_blocks_linking(self, mock_get, mock_post):
        # Create existing local account
        User.objects.create_user(
            email='student@example.edu',
            password='LocalPassword123!',
            full_name='Local Student'
        )
        
        # Mock social profile details
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-access-token'}
        mock_get.return_value.status_code = 200
        mock_get.return_value.json.return_value = self.google_profile
        
        link_data = {
            'email': 'student@example.edu',
            'password': 'WrongPassword!!!',
            'provider': 'google',
            'code': self.oauth_code
        }
        response = self.client.post(self.link_url, link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'invalid_credentials')
        
        # Verify provider flag is NOT modified
        user = User.objects.get(email='student@example.edu')
        self.assertFalse(user.linked_google)

    @patch('requests.post')
    @patch('requests.get')
    def test_account_linking_email_mismatch_fails(self, mock_get, mock_post):
        # Create existing local account
        User.objects.create_user(
            email='student@example.edu',
            password='LocalPassword123!',
            full_name='Local Student'
        )
        
        # Mock social profile details returning different email
        mock_post.return_value.status_code = 200
        mock_post.return_value.json.return_value = {'access_token': 'google-access-token'}
        mock_get.return_value.status_code = 200
        mismatched_profile = self.google_profile.copy()
        mismatched_profile['email'] = 'imposter@example.edu'
        mock_get.return_value.json.return_value = mismatched_profile
        
        link_data = {
            'email': 'student@example.edu',
            'password': 'LocalPassword123!',
            'provider': 'google',
            'code': self.oauth_code
        }
        response = self.client.post(self.link_url, link_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'email_mismatch')
        
        # Verify provider flag is NOT modified
        user = User.objects.get(email='student@example.edu')
        self.assertFalse(user.linked_google)
