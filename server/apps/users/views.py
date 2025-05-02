from django.contrib.auth import get_user_model
from drf_spectacular.utils import extend_schema
from rest_framework import generics, status, viewsets
from rest_framework.decorators import action
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.request import Request
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from server.apps.users.logic.serializers import (
    CustomTokenObtainPairSerializer,
    PasswordResetConfirmSerializer,
    PasswordResetRequestSerializer,
    UserOnboardingSerializer,
    UserRegistrationSerializer,
)
from server.common.api_response import ApiResponse

User = get_user_model()


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
        serializer.save()
        # TODO: Send verification email
        return ApiResponse(serializer.data, status=status.HTTP_201_CREATED)

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
