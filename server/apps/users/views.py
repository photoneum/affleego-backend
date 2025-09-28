from typing import TYPE_CHECKING, Any

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
    UserProfileSerializer,
    UserProfileUpdateSerializer,
    UserRegistrationSerializer,
    VerificationSerializer,
)
from server.apps.users.logic.utils import get_custom_user_model
from server.apps.users.models import VerificationCode
from server.common.api_response import ApiResponse
from server.common.notifications.email import EmailNotificationFactory
from server.common.notifications.telegram import TelegramNotificationFactory
from server.settings.components import config

User = get_custom_user_model()

if TYPE_CHECKING:
    from server.apps.users.models import User as UserType
    from server.apps.users.models import UserOnboarding


@extend_schema(tags=['Authentication'])
class AuthViewSet(viewsets.GenericViewSet):
    permission_classes = (AllowAny,)

    @extend_schema(
        responses={200: UserProfileSerializer},
        description='Get complete user profile data',
        summary='User Profile',
    )
    @action(detail=False, methods=['get'], permission_classes=[IsAuthenticated])
    def profile(self, request: Request) -> Response:
        user = request.user
        serializer = UserProfileSerializer(user)
        return ApiResponse(serializer.data, status=status.HTTP_200_OK)

    @extend_schema(
        request={
            'multipart/form-data': {
                'type': 'object',
                'properties': {
                    'first_name': {'type': 'string'},
                    'last_name': {'type': 'string'},
                    'phone_number': {'type': 'string'},
                    'image': {'type': 'string', 'format': 'binary'},
                    'country': {'type': 'string'},
                },
            }
        },
        responses={200: UserProfileSerializer},
        description=(
            'Update user profile data. The image field accepts binary file uploads. '
            'Use multipart/form-data content type when uploading files.'
        ),
        summary='Update User Profile',
    )
    @action(detail=False, methods=['put'], permission_classes=[IsAuthenticated])
    def update_profile(self, request: Request) -> Response:
        user = request.user
        serializer = UserProfileUpdateSerializer(user, data=request.data, partial=True)
        serializer.is_valid(raise_exception=True)
        serializer.save()
        return ApiResponse(UserProfileSerializer(user).data, status=status.HTTP_200_OK)

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
        verification_code = VerificationCode.generate_code(
            user,
            code_type=VerificationCode.Type.VERIFY_ACCOUNT,
        )

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
        verification_code = VerificationCode.generate_code(
            user,
            code_type=VerificationCode.Type.VERIFY_ACCOUNT,
        )
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
                message='User with this email does not exist.',
                status=status.HTTP_404_NOT_FOUND,
            )

        # Find the verification code
        verification_code = (
            user.verification_codes.filter(
                code=code,
                is_used=False,
                type=VerificationCode.Type.VERIFY_ACCOUNT,
            )
            .order_by('-created_at')
            .first()
        )

        if not verification_code or not verification_code.is_valid():
            return ApiResponse(
                message='Invalid or expired verification code.',
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Mark the code as used
        verification_code.is_used = True
        verification_code.save(update_fields=['is_used'])

        # Activate the user
        user.is_verified = True
        user.is_active = True
        user.save(update_fields=['is_verified', 'is_active'])

        # Delete previous unused verification codes
        VerificationCode.objects.filter(
            user=user,
            is_used=False,
            type=VerificationCode.Type.VERIFY_ACCOUNT,
        ).delete()

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
    @action(detail=False, methods=['post'])
    def onboarding(self, request: Request) -> Response:
        serializer = UserOnboardingSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        onboarding: UserOnboarding = serializer.save()

        context: dict[str, Any] = {
            'user': onboarding.user,
        }
        email = EmailNotificationFactory.create_welcome_email(
            onboarding.user.email,
            context,
        )
        email.send()

        return ApiResponse(
            message='Onboarding completed successfully.',
            status=status.HTTP_200_OK,
        )


@extend_schema(tags=['Authentication'])
class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().post(request)
        return ApiResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Authentication'])
class CustomTokenRefreshView(TokenRefreshView):
    serializer_class = CustomTokenRefreshSerializer

    def post(self, request: Request) -> Response:
        serializer = self.get_serializer(data=request.data)
        if serializer.is_valid():
            return super().post(request)
        return ApiResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
                user = User.objects.get(email=email)
                verification_code = VerificationCode.generate_code(
                    user,
                    code_type=VerificationCode.Type.RESET_PASSWORD,
                )

                context: dict[str, Any] = {
                    'user': user,
                    'verification_url': f'{config("FRONTEND_URL")}/auth/reset-password/?email={user.email}&code={verification_code.code}',  # noqa: E501
                }
                email = EmailNotificationFactory.create_resend_verification_link_email(
                    user.email,
                    context,
                )
                email.send()
                return ApiResponse(
                    message='Password reset email has been sent.',
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return ApiResponse(
                    message='User with this email does not exist.',
                    status=status.HTTP_404_NOT_FOUND,
                )
        return ApiResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
            code = serializer.validated_data['code']

            # Find the verification code
            verification_code = (
                VerificationCode.objects.filter(
                    user__email=email,
                    code=code,
                    is_used=False,
                    type=VerificationCode.Type.RESET_PASSWORD,
                )
                .order_by('-created_at')
                .first()
            )

            if not verification_code or not verification_code.is_valid():
                return ApiResponse(
                    message='Invalid or expired verification code.',
                    status=status.HTTP_400_BAD_REQUEST,
                )

            # Mark the code as used
            verification_code.is_used = True
            verification_code.save(update_fields=['is_used'])

            try:
                user = User.objects.get(email=email)
                user.set_password(new_password)
                user.save()

                # delete previous unused verification codes
                VerificationCode.objects.filter(
                    user__email=email,
                    is_used=False,
                    type=VerificationCode.Type.RESET_PASSWORD,
                ).delete()

                return ApiResponse(
                    message='Password has been reset successfully.',
                    status=status.HTTP_200_OK,
                )
            except User.DoesNotExist:
                return ApiResponse(
                    message='User with this email does not exist.',
                    status=status.HTTP_404_NOT_FOUND,
                )
        return ApiResponse(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


@extend_schema(tags=['Telegram'])
class TelegramViewSet(viewsets.GenericViewSet):
    permission_classes = (IsAuthenticated,)

    @extend_schema(
        request=None,
        responses={200: None},
        description='Send a message to the Telegram channel',
        summary='Send Telegram Message',
    )
    @action(detail=False, methods=['post'])
    def send_message(self, request: Request) -> Response:
        user: UserType = request.user  # type: ignore
        message = f'This user: {user.first_name} {user.last_name} ({user.email}) \
        {user.phone_number or ""} has indicated an interest in joining the Affleego \
        Learn and Club Hub. Kindly act accordingly.'
        tg_notification = TelegramNotificationFactory.create_notification(message)
        tg_notification.send()
        return ApiResponse(
            message='Message sent successfully.',
            status=status.HTTP_200_OK,
        )
