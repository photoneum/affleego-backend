from typing import TYPE_CHECKING, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from server.apps.users.logic.utils import get_custom_user_model
from server.apps.users.models import UserOnboarding

User = get_custom_user_model()

if TYPE_CHECKING:
    from server.apps.users.models import User as UserModel


class UserRegistrationSerializer(serializers.ModelSerializer['UserModel']):
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = User
        fields = ('email', 'password', 'first_name', 'last_name', 'phone_number')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True},
            'email': {'required': True},
        }

    def create(self, validated_data: dict[str, Any]) -> 'UserModel':
        validated_data['email'] = validated_data['email'].lower()
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User needs to verify email
        user.save()
        return user


class ResendVerificationCodeSerializer(serializers.Serializer):
    email = serializers.EmailField(required=True)


class UserOnboardingSerializer(serializers.ModelSerializer['UserOnboarding']):
    user_email = serializers.EmailField(required=True, write_only=True)

    class Meta:
        model = UserOnboarding
        fields = (
            'user_email',
            'brand_name',
            'website',
            'marketing_methods',
            'heard_from',
            'feedback_message',
            'ftds_deliverability_per_month',
            'affliate_experience',
            'type_of_deals_wanted',
        )

    def create(self, validated_data: dict[str, Any]) -> 'UserOnboarding':
        user_email = validated_data.pop('user_email')
        try:
            user = User.objects.get(email=user_email)
        except User.DoesNotExist:
            raise serializers.ValidationError(
                {'user_email': 'User with this email does not exist.'},
                code='user_not_found',
            ) from User.DoesNotExist
        return UserOnboarding.objects.create(user=user, **validated_data)


class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data: dict[str, Any] = super().validate(attrs)
        user: UserModel = self.user  # type: ignore
        if not user.is_verified:
            raise serializers.ValidationError({'email': 'Please verify your email address first.'})

        # add user data to payload
        data['user'] = {
            'email': user.email,
            'first_name': user.first_name,
            'last_name': user.last_name,
            'phone_number': user.phone_number,
            'image_url': user.get_image_url,
        }
        return data


class CustomTokenRefreshSerializer(TokenRefreshSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        # Get user from refresh token
        refresh_token = attrs['refresh']
        refresh = self.token_class(refresh_token)
        user_id = refresh.payload.get('user_id')
        user = User.objects.get(id=user_id)
        if not user.is_verified:
            raise serializers.ValidationError({'email': 'Please verify your email address first.'})
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    code = serializers.CharField(max_length=12)
    password = serializers.CharField(write_only=True, validators=[validate_password])


class VerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""

    email = serializers.EmailField()
    code = serializers.CharField(max_length=12)
