from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
# REMOVE these JWT imports - they're causing the 500 error
# from rest_framework_simplejwt.tokens import RefreshToken
# from rest_framework_simplejwt.views import TokenRefreshView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from .models import UserProfile, MembershipPlan, MembershipHistory
from .serializers import (
    UserRegistrationSerializer, 
    UserLoginSerializer, 
    UserSerializer,
    UserProfileSerializer,
    ChangePasswordSerializer,
    MembershipPlanSerializer,
    MembershipHistorySerializer,
    MembershipUpgradeSerializer
)
from django.conf import settings
from django.contrib.auth.models import User
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode
from django.utils.encoding import force_bytes
from django.core.mail import send_mail
from rest_framework.permissions import AllowAny

User = get_user_model()

# REMOVE all JWT-based views until we fix the dependency issue
# Comment out or remove these views that use JWT:

"""
class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        # REMOVE JWT token creation
        # refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        # REMOVE JWT token creation
        # refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'message': 'Login successful'
        })

class CookieLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        # REMOVE cookie setting for JWT
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        # REMOVE JWT token refresh
        return Response({'error': 'JWT temporarily disabled'})
"""

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        response = Response({'message': 'Logout successful'})
        # REMOVE JWT token blacklisting
        return response
    except Exception as e:
        return Response({'error': 'Logout failed'}, status=status.HTTP_400_BAD_REQUEST)

# KEEP these views - they don't use JWT
class ProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user

class UserProfileUpdateView(generics.RetrieveUpdateAPIView):
    serializer_class = UserProfileSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        profile, created = UserProfile.objects.get_or_create(user=self.request.user)
        return profile

class ChangePasswordView(generics.UpdateAPIView):
    serializer_class = ChangePasswordSerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_object(self):
        return self.request.user
    
    def update(self, request, *args, **kwargs):
        user = self.get_object()
        serializer = self.get_serializer(data=request.data)
        
        if serializer.is_valid():
            if not user.check_password(serializer.validated_data['old_password']):
                return Response({'old_password': ['Wrong password.']}, 
                              status=status.HTTP_400_BAD_REQUEST)
            
            user.set_password(serializer.validated_data['new_password'])
            user.save()
            return Response({'message': 'Password updated successfully'})
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# KEEP membership views - they don't use JWT
class MembershipPlansListView(generics.ListAPIView):
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    permission_classes = [permissions.AllowAny]

class UserMembershipHistoryView(generics.ListAPIView):
    serializer_class = MembershipHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MembershipHistory.objects.filter(user=self.request.user)

# ... (keep all other membership views)

# FIX the create_admin view - remove permission_classes decorator
@csrf_exempt
def create_admin(request):
    """
    Temporary view to create admin user - REMOVE AFTER USE!
    """
    try:
        if request.method == 'POST':
            # Check if admin already exists
            if not User.objects.filter(is_superuser=True).exists():
                User.objects.create_superuser(
                    username='KenBeast',
                    email='thelaydiesden@gmail.com',
                    password='25@laydies#'
                )
                return JsonResponse({'message': 'Admin user created successfully!'})
            return JsonResponse({'message': 'Admin user already exists'})
        return JsonResponse({'error': 'POST method required'}, status=400)
    
    except Exception as e:
        return JsonResponse({
            'error': str(e),
            'message': 'Error creating admin user'
        }, status=500)

# FIX the reset_admin_password view - remove permission_classes decorator
@csrf_exempt
def reset_admin_password(request):
    """
    Reset admin password - creates a new strong password
    """
    try:
        admin_user = User.objects.get(is_superuser=True)
        new_password = 'NewStrongPassword123!@#'
        admin_user.set_password(new_password)
        admin_user.save()
        return JsonResponse({
            'message': 'Admin password reset successfully!',
        })
    except User.DoesNotExist:
        return JsonResponse({'error': 'No admin user found'}, status=400)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=500)