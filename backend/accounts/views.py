from django.conf import settings
from django.contrib.auth import get_user_model, authenticate
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenRefreshSerializer
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError

from accounts.serializers import LoginSerializer, RegisterSerializer, UserDetailSerializer
from accounts.services import OAuthService

User = get_user_model()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)
    return {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
    }

def set_refresh_token_cookie(response, refresh_token):
    response.set_cookie(
        key='refresh_token',
        value=refresh_token,
        httponly=True,
        secure=not settings.DEBUG,
        samesite='Lax',
        path='/api/v1/auth/'
    )

class LoginView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = LoginSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": "validation_error",
                "message": "Invalid input credentials",
                "fields": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email']
        password = serializer.validated_data['password']
        
        user = authenticate(username=email, password=password)
        if not user:
            return Response({
                "code": "invalid_credentials",
                "message": "Invalid email or password"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        tokens = get_tokens_for_user(user)
        response = Response({
            "access": tokens['access'],
            "user": UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
        set_refresh_token_cookie(response, tokens['refresh'])
        return response

class TokenRefreshCookieView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if not refresh_token:
            return Response({
                "code": "token_missing",
                "message": "Refresh token is missing from cookies"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        serializer = TokenRefreshSerializer(data={'refresh': refresh_token})
        try:
            serializer.is_valid(raise_exception=True)
        except (InvalidToken, TokenError):
            return Response({
                "code": "token_invalid",
                "message": "Refresh token is invalid or expired"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        data = serializer.validated_data
        response = Response({
            'access': data['access']
        }, status=status.HTTP_200_OK)
        
        if 'refresh' in data:
            set_refresh_token_cookie(response, data['refresh'])
            
        return response

class RegisterView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        serializer = RegisterSerializer(data=request.data)
        if not serializer.is_valid():
            return Response({
                "code": "validation_error",
                "message": "Invalid registration input",
                "fields": serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = serializer.validated_data['email'].lower().strip()
        
        # Check collision
        existing_user = User.objects.filter(email=email).first()
        if existing_user:
            if existing_user.has_usable_password() or existing_user.provider == 'local':
                # Local user exists
                return Response({
                    "code": "email_registered",
                    "message": "An account with this email already exists."
                }, status=status.HTTP_400_BAD_REQUEST)
            else:
                # OAuth-only user exists
                return Response({
                    "code": "account_collision",
                    "message": "An account with this email exists via social login. Please authenticate to link this account.",
                    "email": email,
                    "provider": existing_user.provider
                }, status=status.HTTP_409_CONFLICT)
        
        # Save user if no collision
        user = serializer.save()
        tokens = get_tokens_for_user(user)
        
        response = Response({
            "access": tokens['access'],
            "user": UserDetailSerializer(user).data
        }, status=status.HTTP_201_CREATED)
        
        set_refresh_token_cookie(response, tokens['refresh'])
        return response

class BaseOAuthCallbackView(APIView):
    permission_classes = []
    provider_name = None

    def post(self, request, *args, **kwargs):
        code = request.data.get('code')
        if not code:
            return Response({
                "code": "code_missing",
                "message": "OAuth authorization code is missing."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            if self.provider_name == 'google':
                profile = OAuthService.verify_google_token(code)
            elif self.provider_name == 'github':
                profile = OAuthService.verify_github_token(code)
            else:
                return Response({"message": "Invalid provider"}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": "oauth_verification_failed",
                "message": str(e)
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        email = profile['email'].lower().strip()
        provider_id = profile['provider_id']
        name = profile['name']
        avatar_url = profile['avatar_url']
        
        user = User.objects.filter(email=email).first()
        if not user:
            # Create a new user from OAuth signup
            user = User.objects.create_user(
                email=email,
                password=None,
                full_name=name,
                avatar_url=avatar_url,
                provider=self.provider_name,
                linked_google=(self.provider_name == 'google'),
                linked_github=(self.provider_name == 'github')
            )
        else:
            is_linked = user.linked_google if self.provider_name == 'google' else user.linked_github
            if not is_linked:
                # Local collision detected: block auto-login
                return Response({
                    "code": "account_collision",
                    "message": f"An account with this email already exists. Please verify your password to link this {self.provider_name} account.",
                    "email": email,
                    "provider": self.provider_name
                }, status=status.HTTP_409_CONFLICT)
        
        # Valid login/signup
        tokens = get_tokens_for_user(user)
        response = Response({
            "access": tokens['access'],
            "user": UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
        set_refresh_token_cookie(response, tokens['refresh'])
        return response

class GoogleOAuthCallbackView(BaseOAuthCallbackView):
    provider_name = 'google'

class GitHubOAuthCallbackView(BaseOAuthCallbackView):
    provider_name = 'github'

class AccountLinkConfirmView(APIView):
    permission_classes = []

    def post(self, request, *args, **kwargs):
        email = request.data.get('email')
        password = request.data.get('password')
        provider = request.data.get('provider')
        code = request.data.get('code')

        if not all([email, password, provider, code]):
            return Response({
                "code": "missing_fields",
                "message": "All fields (email, password, provider, code) are required."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        email = email.lower().strip()

        # Step 1: Verify OAuth code to ensure student owns the social account
        try:
            if provider == 'google':
                profile = OAuthService.verify_google_token(code)
            elif provider == 'github':
                profile = OAuthService.verify_github_token(code)
            else:
                return Response({
                    "code": "invalid_provider",
                    "message": "Invalid provider name."
                }, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({
                "code": "oauth_verification_failed",
                "message": f"Social verification failed: {str(e)}"
            }, status=status.HTTP_401_UNAUTHORIZED)
        
        # Step 2: Ensure email matches the OAuth email
        if profile['email'].lower().strip() != email:
            return Response({
                "code": "email_mismatch",
                "message": "The email from the social provider does not match the requested email."
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Step 3: Validate local password credentials
        user = authenticate(username=email, password=password)
        if not user:
            return Response({
                "code": "invalid_credentials",
                "message": "Invalid local password. Linking failed."
            }, status=status.HTTP_410_UNAUTHORIZED if False else status.HTTP_401_UNAUTHORIZED)
        
        # Step 4: Link and Save
        if provider == 'google':
            user.linked_google = True
        elif provider == 'github':
            user.linked_github = True
        
        user.save()

        # Step 5: Return active JWT session
        tokens = get_tokens_for_user(user)
        response = Response({
            "access": tokens['access'],
            "user": UserDetailSerializer(user).data
        }, status=status.HTTP_200_OK)
        
        set_refresh_token_cookie(response, tokens['refresh'])
        return response
