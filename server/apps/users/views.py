from typing import Any

from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView

from server.apps.users.logic.serializers import (
    CustomTokenObtainPairSerializer,
    CustomTokenRefreshSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    ResendVerificationCodeSerializer,
    UserOnboardingSerializer,
    UserRegistrationSerializer,
    VerificationSerializer,
)
from server.apps.users.logic.utils import get_custom_user_model
from server.apps.users.models import VerificationCode
from server.common.api_response import ApiResponse
from server.common.notifications.email import EmailNotificationFactory
from server.settings.components import config

User = get_custom_user_model()


@extend_schema(tags=['Authentication'])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @extend_schema(
        request=UserRegistrationSerializer,
        responses={201: UserRegistrationSerializer},
        description='Register a new user account',
        summary='User Registration',
    )
    @action(detail=False, methods=['post'])
    def register(self, request: Request) -> Response:
        serializer = UserRegistrationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = serializer.save()

        # Generate verification code
        verification_code = VerificationCode.generate_code(user)

        context: dict[str, Any] = {
            'user': user,
            'verification_url': f'{config("FRONTEND_URL")}/auth/verify-account/?email={user.email}&code={verification_code.code}',  # noqa: E501
        }
        email = EmailNotificationFactory.create_verify_user_email(
            user.email,
            context,
        )
        email.send()
        return ApiResponse(serializer.data, status=status.HTTP_201_CREATED)

    @extend_schema(
        request=ResendVerificationCodeSerializer,
        responses={200: None},
        description='Resend verification code',
        summary='Resend Verification Code',
    )
    @action(detail=False, methods=['post'], url_path='resend-verification-code')
    def resend_verification_code(self, request: Request) -> Response:
        serializer = ResendVerificationCodeSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = User.objects.get(email=email)
        verification_code = VerificationCode.generate_code(user)
        context: dict[str, Any] = {
            'user': user,
            'verification_url': f'{config("FRONTEND_URL")}/auth/verify-account/?email={user.email}&code={verification_code.code}',  # noqa: E501
        }
        email = EmailNotificationFactory.create_resend_verification_link_email(
            user.email,
            context,
        )
        email.send()
        return ApiResponse(
            message='Verification code has been sent.',
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=VerificationSerializer,
        responses={200: None},
        description='Verify user email with verification code',
        summary='Verify User Email',
    )
    @action(detail=False, methods=['post'])
    def verify(self, request: Request) -> Response:
        serializer = VerificationSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        email = serializer.validated_data['email']
        code = serializer.validated_data['code']

        try:
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            return ApiResponse(
                {'detail': 'User with this email does not exist.'},
                status=status.HTTP_404_NOT_FOUND,
            )

        # Find the verification code
        # verification_code = (
        #     user.verification_codes.filter(
        #         code=code,
        #         is_used=False,
        #     )
        #     .order_by('-created_at')
        #     .first()
        # )

        verification_code = (
            user.verification_codes.filter(
                code=code,
                is_used=False,
            )
            .order_by('-created_at')
            .first()
        )

        if not verification_code or not verification_code.is_valid():
            return ApiResponse(
                {'detail': 'Invalid or expired verification code.'},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark the code as used
        verification_code.is_used = True
        verification_code.save(update_fields=['is_used'])

        # Activate the user
        user.is_verified = True
        user.is_active = True
        user.save(update_fields=['is_verified', 'is_active'])

        return ApiResponse(
            message='Email verified successfully. You can now login.',
            status=status.HTTP_200_OK,
        )

    @extend_schema(
        request=UserOnboardingSerializer,
        responses={200: UserOnboardingSerializer},
        description='Complete user onboarding process',
        summary='User Onboarding',
    )
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def onboarding(self, request: Request) -> Response:
        serializer = UserOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        # TODO: Save onboarding data to user profile or related model
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().post(request)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().post(request)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class PasswordResetRequestView(generics.GenericAPIView):
    serializer_class = PasswordResetRequestSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: None},
        description='Request password reset email',
        summary='Request Password Reset',
    )
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            try:
                User.objects.get(email=email)
                # TODO: Send password reset email
                return Response(
                    {'detail': 'Password reset email has been sent.'}, status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User with this email does not exist.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class PasswordResetConfirmView(generics.GenericAPIView):
    serializer_class = PasswordResetConfirmSerializer
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: None},
        description='Reset password with new password',
        summary='Reset Password',
    )
    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            email = serializer.validated_data['email']
            new_password = serializer.validated_data['password']
            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()
                return Response(
                    {'detail': 'Password has been reset successfully.'}, status=status.HTTP_200_OK
                )
            except User.DoesNotExist:
                return Response(
                    {'detail': 'User with this email does not exist.'},
                    status=status.HTTP_404_NOT_FOUND,
                )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
