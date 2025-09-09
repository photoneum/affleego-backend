from django.urls import include, path
from rest_framework.routers import DefaultRouter

from server.apps.users.views import (
    AuthViewSet,
    CustomTokenObtainPairView,
    CustomTokenRefreshView,
    PasswordResetConfirmView,
    PasswordResetRequestView,
    TelegramViewSet,
)

app_name = 'users'

router = DefaultRouter(trailing_slash='')
router.register('auth', AuthViewSet, basename='auth')
router.register('telegram', TelegramViewSet, basename='telegram')

urlpatterns = [
    path('', include(router.urls)),
    path('auth/login', CustomTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('auth/refresh', CustomTokenRefreshView.as_view(), name='token_refresh'),
    path('auth/password-reset', PasswordResetRequestView.as_view(), name='password_reset'),
    path(
        'auth/password-reset/confirm',
        PasswordResetConfirmView.as_view(),
        name='password_reset_confirm',
    ),
]
