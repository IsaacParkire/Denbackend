from rest_framework import serializers
from django.contrib.auth import authenticate
from django.contrib.auth.password_validation import validate_password
from .models import User, UserProfile, MembershipPlan, MembershipHistory

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, validators=[validate_password])
    password_confirm = serializers.CharField(write_only=True)
    membership_type = serializers.ChoiceField(choices=User.MEMBERSHIP_CHOICES, default='basic')
    
    class Meta:
        model = User
        fields = (
            'email', 'first_name', 'last_name', 'phone_number', 'date_of_birth', 
            'password', 'password_confirm', 'membership_type'
        )
    
    def validate(self, attrs):
        if attrs['password'] != attrs['password_confirm']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})
        return attrs
    
    def create(self, validated_data):
        validated_data.pop('password_confirm')
        membership_type = validated_data.pop('membership_type', 'basic')
        
        user = User.objects.create_user(**validated_data)
        user.membership_type = membership_type
        
        # Set membership status based on type
        if membership_type in ['premium', 'vip']:
            user.membership_status = 'pending'  # Requires payment
        else:
            user.membership_status = 'active'  # Basic is free
            
        user.save()
        UserProfile.objects.create(user=user)
        return user

class UserLoginSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True)
    
    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')
        
        if email and password:
            user = authenticate(request=self.context.get('request'), email=email, password=password)
            if not user:
                raise serializers.ValidationError('Invalid credentials.')
            if not user.is_active:
                raise serializers.ValidationError('User account is disabled.')
            attrs['user'] = user
        else:
            raise serializers.ValidationError('Must include email and password.')
        
        return attrs

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = '__all__'
        read_only_fields = ('user', 'loyalty_points', 'created_at', 'updated_at')

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer(read_only=True)
    membership_display_name = serializers.CharField(read_only=True)
    is_membership_active = serializers.BooleanField(read_only=True)
    
    class Meta:
        model = User
        fields = (
            'id', 'email', 'first_name', 'last_name', 'phone_number', 
            'date_of_birth', 'gender', 'address', 'date_joined',
            'membership_type', 'membership_status', 'membership_start_date', 
            'membership_end_date', 'membership_display_name', 'is_membership_active',
            'profile'
        )
        read_only_fields = (
            'id', 'date_joined', 'membership_start_date', 'membership_end_date'
        )

class ChangePasswordSerializer(serializers.Serializer):
    old_password = serializers.CharField(required=True)
    new_password = serializers.CharField(required=True, validators=[validate_password])

class MembershipPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = MembershipPlan
        fields = '__all__'

class MembershipHistorySerializer(serializers.ModelSerializer):
    plan_name = serializers.CharField(source='plan.name', read_only=True)
    plan_type = serializers.CharField(source='plan.plan_type', read_only=True)
    
    class Meta:
        model = MembershipHistory
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class MembershipUpgradeSerializer(serializers.Serializer):
    plan_type = serializers.ChoiceField(choices=User.MEMBERSHIP_CHOICES)
    payment_method = serializers.CharField(max_length=50)
    payment_reference = serializers.CharField(max_length=100, required=False)
    duration_months = serializers.IntegerField(default=1, min_value=1, max_value=12)
