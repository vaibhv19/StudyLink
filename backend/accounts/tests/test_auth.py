from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

User = get_user_model()

class AuthenticationTests(APITestCase):
    def setUp(self):
        self.register_url = reverse('accounts:register')
        self.login_url = reverse('accounts:login')
        self.refresh_url = reverse('accounts:token_refresh')
        
        self.user_data = {
            'email': 'student@example.edu',
            'password': 'StrongPassword123!',
            'full_name': 'Study Linker'
        }
        
    def test_registration_success(self):
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'student@example.edu')
        self.assertEqual(response.data['user']['full_name'], 'Study Linker')
        
        # Verify HttpOnly refresh token cookie is set
        self.assertIn('refresh_token', response.cookies)
        cookie = response.cookies['refresh_token']
        self.assertTrue(cookie['httponly'])
        self.assertEqual(cookie['path'], '/api/v1/auth/')

    def test_registration_invalid_data(self):
        # Weak password (no number/special char)
        invalid_data = self.user_data.copy()
        invalid_data['password'] = 'weakpass'
        response = self.client.post(self.register_url, invalid_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'validation_error')

    def test_registration_local_email_collision(self):
        # Create user
        User.objects.create_user(
            email='student@example.edu',
            password='Password123!',
            full_name='Existing Student'
        )
        # Try registering again
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(response.data['code'], 'email_registered')

    def test_registration_oauth_email_collision(self):
        # Create OAuth user without password
        User.objects.create_user(
            email='student@example.edu',
            password=None,
            full_name='OAuth Student',
            provider='google',
            linked_google=True
        )
        # Try registering again
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_409_CONFLICT)
        self.assertEqual(response.data['code'], 'account_collision')
        self.assertEqual(response.data['provider'], 'google')

    def test_login_success(self):
        # Create user
        User.objects.create_user(
            email='student@example.edu',
            password='StrongPassword123!',
            full_name='Study Linker'
        )
        # Login
        login_data = {
            'email': 'student@example.edu',
            'password': 'StrongPassword123!'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertEqual(response.data['user']['email'], 'student@example.edu')
        self.assertIn('refresh_token', response.cookies)

    def test_login_invalid_credentials(self):
        # Try logging in before user is created
        login_data = {
            'email': 'student@example.edu',
            'password': 'wrongpassword'
        }
        response = self.client.post(self.login_url, login_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'invalid_credentials')

    def test_token_refresh_success(self):
        # Register to get cookie
        response = self.client.post(self.register_url, self.user_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        
        # Clear access token to ensure we don't rely on it
        self.client.credentials()
        
        # Call refresh
        response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)

    def test_token_refresh_missing_cookie(self):
        # Call refresh directly without cookie
        response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_missing')

    def test_token_refresh_invalid_cookie(self):
        self.client.cookies['refresh_token'] = 'invalid-token-value'
        response = self.client.post(self.refresh_url, format='json')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
        self.assertEqual(response.data['code'], 'token_invalid')
