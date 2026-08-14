import os
import requests
from django.conf import settings
from rest_framework.exceptions import AuthenticationFailed

class OAuthService:
    @staticmethod
    def verify_google_token(auth_code):
        client_id = getattr(settings, 'GOOGLE_CLIENT_ID', 'placeholder-google-client-id')
        client_secret = getattr(settings, 'GOOGLE_CLIENT_SECRET', 'placeholder-google-client-secret')
        redirect_uri = getattr(settings, 'GOOGLE_REDIRECT_URI', 'http://localhost:5173/auth/google/callback')

        token_url = "https://oauth2.googleapis.com/token"
        payload = {
            'code': auth_code,
            'client_id': client_id,
            'client_secret': client_secret,
            'redirect_uri': redirect_uri,
            'grant_type': 'authorization_code'
        }
        try:
            response = requests.post(token_url, data=payload, timeout=10)
            if response.status_code != 200:
                raise AuthenticationFailed("Failed to exchange code for Google token.")
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                raise AuthenticationFailed("Google token exchange did not return an access token.")
            
            user_info_url = "https://www.googleapis.com/oauth2/v3/userinfo"
            headers = {'Authorization': f'Bearer {access_token}'}
            user_info_res = requests.get(user_info_url, headers=headers, timeout=10)
            if user_info_res.status_code != 200:
                raise AuthenticationFailed("Failed to fetch user profile from Google.")
            
            user_info = user_info_res.json()
            return {
                'email': user_info.get('email'),
                'provider_id': user_info.get('sub'),
                'name': user_info.get('name', ''),
                'avatar_url': user_info.get('picture', '')
            }
        except requests.exceptions.Timeout:
            raise AuthenticationFailed("Connection timeout while contacting Google OAuth.")
        except requests.exceptions.RequestException:
            raise AuthenticationFailed("Network error during Google OAuth verification.")

    @staticmethod
    def verify_github_token(auth_code):
        client_id = getattr(settings, 'GITHUB_CLIENT_ID', 'placeholder-github-client-id')
        client_secret = getattr(settings, 'GITHUB_CLIENT_SECRET', 'placeholder-github-client-secret')

        token_url = "https://github.com/login/oauth/access_token"
        headers = {'Accept': 'application/json'}
        payload = {
            'client_id': client_id,
            'client_secret': client_secret,
            'code': auth_code
        }
        try:
            response = requests.post(token_url, json=payload, headers=headers, timeout=10)
            if response.status_code != 200:
                raise AuthenticationFailed("Failed to exchange code for GitHub token.")
            
            token_data = response.json()
            access_token = token_data.get('access_token')
            if not access_token:
                raise AuthenticationFailed("GitHub token exchange did not return an access token.")

            user_url = "https://api.github.com/user"
            headers = {
                'Authorization': f'token {access_token}',
                'Accept': 'application/json'
            }
            user_res = requests.get(user_url, headers=headers, timeout=10)
            if user_res.status_code != 200:
                raise AuthenticationFailed("Failed to fetch user profile from GitHub.")
            
            user_info = user_res.json()
            
            email = user_info.get('email')
            if not email:
                emails_url = "https://api.github.com/user/emails"
                emails_res = requests.get(emails_url, headers=headers, timeout=10)
                if emails_res.status_code == 200:
                    for email_data in emails_res.json():
                        if email_data.get('primary') and email_data.get('verified'):
                            email = email_data.get('email')
                            break
            
            if not email:
                raise AuthenticationFailed("Unable to retrieve verified primary email from GitHub.")

            return {
                'email': email,
                'provider_id': str(user_info.get('id')),
                'name': user_info.get('name') or user_info.get('login', ''),
                'avatar_url': user_info.get('avatar_url', '')
            }
        except requests.exceptions.Timeout:
            raise AuthenticationFailed("Connection timeout while contacting GitHub OAuth.")
        except requests.exceptions.RequestException:
            raise AuthenticationFailed("Network error during GitHub OAuth verification.")
