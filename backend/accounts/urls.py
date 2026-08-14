from django.urls import path
from accounts.views import (
    RegisterView, 
    LoginView, 
    TokenRefreshCookieView,
    GoogleOAuthCallbackView,
    GitHubOAuthCallbackView,
    AccountLinkConfirmView
)

app_name = 'accounts'

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshCookieView.as_view(), name='token_refresh'),
    path('social/google/', GoogleOAuthCallbackView.as_view(), name='social_google'),
    path('social/github/', GitHubOAuthCallbackView.as_view(), name='social_github'),
    path('social/link-confirm/', AccountLinkConfirmView.as_view(), name='social_link_confirm'),
]
