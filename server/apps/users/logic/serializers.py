from typing import TYPE_CHECKING, Any

from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework_simplejwt.serializers import (
    TokenObtainPairSerializer,
    TokenRefreshSerializer,
)

from server.apps.users.logic.utils import get_custom_user_model

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
        user = User.objects.create_user(**validated_data)
        user.is_active = False  # User needs to verify email
        user.save()
        return user


class UserOnboardingSerializer(serializers.Serializer):
    brand_name = serializers.CharField(max_length=255)
    website = serializers.URLField(required=False, allow_blank=True)
    marketing_methods = serializers.ListField(
        child=serializers.CharField(max_length=100), required=False
    )
    heard_from = serializers.CharField(max_length=255)
    feedback_message = serializers.CharField(required=False, allow_blank=True)


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
        if not self.user.is_verified:  # type: ignore
            raise serializers.ValidationError({'email': 'Please verify your email address first.'})
        return data


class PasswordResetRequestSerializer(serializers.Serializer):
    email = serializers.EmailField()


class PasswordResetConfirmSerializer(serializers.Serializer):
    email = serializers.EmailField()
    password = serializers.CharField(write_only=True, validators=[validate_password])


class VerificationSerializer(serializers.Serializer):
    """Serializer for email verification."""

    email = serializers.EmailField()
    code = serializers.CharField(max_length=6)
