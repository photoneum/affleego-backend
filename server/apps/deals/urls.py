from django.urls import include, path
from rest_framework.routers import DefaultRouter

from server.apps.deals.views import DealViewSet

app_name = 'deals'

router = DefaultRouter(trailing_slash='')
router.register('deals', DealViewSet, basename='deals')

urlpatterns = [
    path('', include(router.urls)),
]
