from rest_framework import generics, status, permissions
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework_simplejwt.tokens import RefreshToken
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
from rest_framework_simplejwt.views import TokenRefreshView
from django.conf import settings

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserRegistrationSerializer
    permission_classes = [permissions.AllowAny]
    
    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'User registered successfully'
        }, status=status.HTTP_201_CREATED)

class LoginView(generics.GenericAPIView):
    serializer_class = UserLoginSerializer
    permission_classes = [permissions.AllowAny]
    
    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.validated_data['user']
        
        refresh = RefreshToken.for_user(user)
        return Response({
            'user': UserSerializer(user).data,
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'message': 'Login successful'
        })

class CookieLoginView(LoginView):
    def post(self, request, *args, **kwargs):
        response = super().post(request, *args, **kwargs)
        if response.status_code == 200:
            refresh = response.data.get('refresh')
            if refresh:
                response.set_cookie(
                    key='refresh_token',
                    value=refresh,
                    httponly=True,
                    secure=not settings.DEBUG,  # True in production
                    samesite='Lax',
                    max_age=365*24*60*60,
                    path='/api/accounts/token/refresh/'
                )
                if 'refresh' in response.data:
                    del response.data['refresh']
        return response

class CookieTokenRefreshView(TokenRefreshView):
    def post(self, request, *args, **kwargs):
        refresh_token = request.COOKIES.get('refresh_token')
        if refresh_token:
            request.data['refresh'] = refresh_token
        response = super().post(request, *args, **kwargs)
        return response

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

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def logout_view(request):
    try:
        response = Response({'message': 'Logout successful'})
        response.delete_cookie('refresh_token', path='/api/accounts/token/refresh/')
        refresh_token = request.COOKIES.get('refresh_token') or request.data.get('refresh')
        if refresh_token:
            try:
                token = RefreshToken(refresh_token)
                token.blacklist()
            except Exception:
                pass
        return response
    except Exception as e:
        return Response({'error': 'Invalid token'}, status=status.HTTP_400_BAD_REQUEST)

# Membership Views
class MembershipPlansListView(generics.ListAPIView):
    """Get all available membership plans"""
    queryset = MembershipPlan.objects.filter(is_active=True)
    serializer_class = MembershipPlanSerializer
    permission_classes = [permissions.AllowAny]

class UserMembershipHistoryView(generics.ListAPIView):
    """Get user's membership history"""
    serializer_class = MembershipHistorySerializer
    permission_classes = [permissions.IsAuthenticated]
    
    def get_queryset(self):
        return MembershipHistory.objects.filter(user=self.request.user)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def upgrade_membership(request):
    """Upgrade user membership after successful payment"""
    serializer = MembershipUpgradeSerializer(data=request.data)
    
    if serializer.is_valid():
        user = request.user
        plan_type = serializer.validated_data['plan_type']
        payment_method = serializer.validated_data['payment_method']
        payment_reference = serializer.validated_data.get('payment_reference', '')
        duration_months = serializer.validated_data['duration_months']
        
        try:
            # Get the membership plan
            plan = MembershipPlan.objects.get(plan_type=plan_type, is_active=True)
            
            # Calculate total amount
            total_amount = plan.price * duration_months
            
            # Create membership history record
            membership_history = MembershipHistory.objects.create(
                user=user,
                plan=plan,
                status='active',
                start_date=timezone.now(),
                end_date=timezone.now() + timedelta(days=30 * duration_months),
                payment_amount=total_amount,
                payment_method=payment_method,
                payment_reference=payment_reference,
                payment_date=timezone.now()
            )
            
            # Upgrade user membership
            user.upgrade_membership(plan_type, duration_months)
            
            return Response({
                'message': 'Membership upgraded successfully',
                'user': UserSerializer(user).data,
                'membership_history': MembershipHistorySerializer(membership_history).data
            })
            
        except MembershipPlan.DoesNotExist:
            return Response({'error': 'Invalid membership plan'}, status=status.HTTP_400_BAD_REQUEST)
        except Exception as e:
            return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
    
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

@api_view(['POST'])
@permission_classes([permissions.IsAuthenticated])
def cancel_membership(request):
    """Cancel user's current membership"""
    user = request.user
    
    if user.membership_type == 'basic':
        return Response({'error': 'Basic membership cannot be cancelled'}, status=status.HTTP_400_BAD_REQUEST)
    
    # Update current membership history to cancelled
    current_membership = MembershipHistory.objects.filter(
        user=user,
        status='active'
    ).first()
    
    if current_membership:
        current_membership.status = 'cancelled'
        current_membership.save()
    
    # Downgrade user to basic
    user.cancel_membership()
    
    return Response({
        'message': 'Membership cancelled successfully',
        'user': UserSerializer(user).data
    })

@api_view(['GET'])
@permission_classes([permissions.IsAuthenticated])
def membership_status(request):
    """Get user's current membership status and privileges"""
    user = request.user
    
    # Get current membership plan details
    try:
        current_plan = MembershipPlan.objects.get(plan_type=user.membership_type, is_active=True)
        plan_data = MembershipPlanSerializer(current_plan).data
    except MembershipPlan.DoesNotExist:
        plan_data = None
    
    # Get current active membership history
    current_membership_history = MembershipHistory.objects.filter(
        user=user,
        status='active'
    ).first()
    
    return Response({
        'user': UserSerializer(user).data,
        'current_plan': plan_data,
        'current_membership_history': MembershipHistorySerializer(current_membership_history).data if current_membership_history else None,
        'privileges': {
            'her_secrets_access': current_plan.her_secrets_access if current_plan else False,
            'premium_events_access': current_plan.premium_events_access if current_plan else False,
            'vip_events_access': current_plan.vip_events_access if current_plan else False,
            'priority_booking': current_plan.priority_booking if current_plan else False,
            'premium_gallery_access': current_plan.premium_gallery_access if current_plan else False,
            'vip_gallery_access': current_plan.vip_gallery_access if current_plan else False,
            'custom_experiences': current_plan.custom_experiences if current_plan else False,
            'concierge_service': current_plan.concierge_service if current_plan else False,
            'private_events': current_plan.private_events if current_plan else False,
        }
    })