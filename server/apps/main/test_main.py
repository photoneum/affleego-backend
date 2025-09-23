from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from server.apps.main.models import CommunityStats
from server.apps.users.models import User


class CommunityStatsModelTest(APITestCase):
    def test_create_community_stats(self):
        stats = CommunityStats.objects.create(
            weekly_ftds=10,
            top_geo='US',
            total_affiliates=100,
            total_deals=50,
            week_starting='2025-09-15',
        )
        self.assertEqual(stats.weekly_ftds, 10)
        self.assertEqual(stats.top_geo, 'US')
        self.assertEqual(stats.total_affiliates, 100)
        self.assertEqual(stats.total_deals, 50)
        self.assertEqual(str(stats.week_starting), '2025-09-15')


class DashboardViewSetTest(APITestCase):
    def setUp(self):
        print('TEST USER MODEL:', User.__module__, User.__name__)

        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123',
            first_name='Test',
            last_name='User',
            is_verified=True,
            phone_number='+1234567890',
            timezone='UTC',
            locale='en',
        )
        self.client.force_authenticate(user=self.user)
        CommunityStats.objects.create(
            weekly_ftds=5,
            top_geo='UK',
            total_affiliates=20,
            total_deals=10,
            week_starting='2025-09-15',
        )

    def test_dashboard_overview(self):
        url = reverse('main:dashboard-overview')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('RESPONSE DATA:', response.data)
        # Adjust assertions after inspecting output
