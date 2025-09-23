from django.urls import include, path
from rest_framework.routers import DefaultRouter

from server.apps.main.views import DashboardViewSet

app_name = 'main'

router = DefaultRouter(trailing_slash='')
router.register('dashboard', DashboardViewSet, basename='dashboard')

urlpatterns = [
    path('', include(router.urls)),
]
