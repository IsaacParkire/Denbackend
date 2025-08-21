from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('cookie-login/', views.CookieLoginView.as_view(), name='cookie_login'),
    path('token/refresh/', views.CookieTokenRefreshView.as_view(), name='token_refresh'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('profile/update/', views.UserProfileUpdateView.as_view(), name='profile_update'),
    path('change-password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('logout/', views.logout_view, name='logout'),
    path('membership/plans/', views.MembershipPlansListView.as_view(), name='membership_plans'),
    path('membership/history/', views.UserMembershipHistoryView.as_view(), name='membership_history'),
    path('membership/upgrade/', views.upgrade_membership, name='upgrade_membership'),
    path('membership/cancel/', views.cancel_membership, name='cancel_membership'),
    path('membership/status/', views.membership_status, name='membership_status'),
]