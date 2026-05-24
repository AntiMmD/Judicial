from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()

class JWTAuthTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.data = {
        'phonenumber' : '12345678911',
        'password': 'testpass123'
        }

        cls.user= User.objects.create_user(**cls.data)
        
    def setUp(self):
        super().setUp()
        self.client = APIClient()
        
    
    def test_valid_refresh_token_returns_new_access_token(self):
        response = self.client.post(
            reverse('Accounts:login'),
            data = self.data,
            format="json",
        )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn("refresh", response.data)       

        refresh_token = response.data["refresh"]
        response = self.client.post(
                reverse('Accounts:token_refresh'),
                data={"refresh": refresh_token},
                format="json",
            )

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(response.data["access"])