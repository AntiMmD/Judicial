from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

class JWTAuthTests(TestCase):
    def setUp(self):
        super().setUp()

        self.user = get_user_model().objects.create_user(
            phonenumber = '12345678911',
            password = 'testpass123'
        )
        self.data = {
                'phonenumber' : '12345678911',
                'password': 'testpass123'
            }
        self.client = APIClient()
    
    def test_authenticated_users_can_get_token(self):
        response = self.client.post(
            reverse('user:token_obtain_pair'),
            data = self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_users_can_refresh_token(self):
        response = self.client.post(
            reverse('user:token_obtain_pair'),
            data = self.data,
            format="json",
        )
        
        refresh_token = response.data["refresh"]
        response = self.client.post(
                reverse('user:token_refresh'),
                data={"refresh": refresh_token},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
