from django.urls import path
from .views import (
    # REMOVE these JWT views (they don't exist anymore):
    # RegisterView,
    # LoginView,
    # CookieLoginView, 
    # CookieTokenRefreshView,
    
    # KEEP these views:
    ProfileView,
    UserProfileUpdateView,
    ChangePasswordView,
    logout_view,
    MembershipPlansListView,
    UserMembershipHistoryView,
    upgrade_membership,
    cancel_membership,
    membership_status,
    create_admin,
    reset_admin_password
)
from .health import health_check
from dj_rest_auth.registration.views import SocialLoginView
from allauth.socialaccount.providers.google.views import GoogleOAuth2Adapter
from allauth.socialaccount.providers.apple.views import AppleOAuth2Adapter

class GoogleLogin(SocialLoginView):
    adapter_class = GoogleOAuth2Adapter

class AppleLogin(SocialLoginView):
    adapter_class = AppleOAuth2Adapter

urlpatterns = [
    path('health/', health_check, name='health-check'),
    
    # REMOVE these JWT routes (commented out):
    # path('register/', RegisterView.as_view(), name='user-register'),
    # path('login/', CookieLoginView.as_view(), name='user-login'),
    # path('token/refresh/', CookieTokenRefreshView.as_view(), name='token-refresh'),
    
    path('logout/', logout_view, name='user-logout'),
    path('profile/', ProfileView.as_view(), name='user-profile'),
    path('profile/update/', UserProfileUpdateView.as_view(), name='user-profile-update'),
    path('change-password/', ChangePasswordView.as_view(), name='change-password'),
    
    # Membership endpoints
    path('membership/plans/', MembershipPlansListView.as_view(), name='membership-plans'),
    path('membership/history/', UserMembershipHistoryView.as_view(), name='membership-history'),
    path('membership/upgrade/', upgrade_membership, name='membership-upgrade'),
    path('membership/cancel/', cancel_membership, name='membership-cancel'),
    path('membership/status/', membership_status, name='membership-status'),

    # Social login endpoints
    path('oauth/google/login/', GoogleLogin.as_view(), name='google_login'),
    path('oauth/apple/login/', AppleLogin.as_view(), name='apple_login'),

    # Admin creation endpoint
    path('create-admin/', create_admin, name='create_admin'),

    # Admin password reset endpoint
    path('reset-admin-password/', reset_admin_password, name='reset_admin_password'),
]