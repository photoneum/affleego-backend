from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase

from server.apps.users.models import User


class AuthViewSetProfileTest(APITestCase):
    def setUp(self):
        print('TEST USER MODEL:', User.__module__, User.__name__)
        self.user = User.objects.create_user(
            username='profileuser',
            email='profile@example.com',
            password='testpass123',
            first_name='Profile',
            last_name='User',
            is_verified=True,
            phone_number='+1234567890',
            timezone='UTC',
            locale='en',
        )
        self.client.force_authenticate(user=self.user)

    def test_get_profile(self):
        url = reverse('users:auth-profile')
        response = self.client.get(url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        print('RESPONSE DATA:', response.data)
        # Adjust assertions after inspecting output

    def test_update_profile(self):
        url = reverse('users:auth-update-profile')
        data = {'first_name': 'Updated', 'locale': 'fr'}
        response = self.client.put(url, data)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['data']['first_name'], 'Updated')
        self.assertEqual(response.data['data']['locale'], 'fr')
