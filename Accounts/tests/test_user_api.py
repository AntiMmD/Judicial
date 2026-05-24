from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

User = get_user_model()
SIGNUP_URL = reverse('Accounts:sign-up')


def create_user(**params):
    return User.objects.create_user(**params)

class PublicUserApiTests(TestCase):

    def setUp(self):
        self.client = APIClient()
    
    def test_create_user_successful(self):
        payload ={
            'phonenumber':'09101010101',
            'password':'testpass1234',
            'first_name':'Test Name',
            'last_name': 'Test Surname'
        }
        response = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        user = User.objects.get(phonenumber = payload['phonenumber'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',response.data)

    def test_user_with_phonenumber_exists_error(self):
        payload ={
            'phonenumber':'09101010101',
            'password':'testpass1234',
            'first_name':'Test Name',
            'last_name': 'Test Surname',
        }
        create_user(**payload)
        response = self.client.post(SIGNUP_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        payload ={
            'phonenumber':'09101010101',
            'password':'p23',
            'first_name':'Test Name',
            'last_name': 'Test Surname',            
        }
        response = self.client.post(SIGNUP_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = User.objects.filter(phonenumber = payload['phonenumber']).exists()
        self.assertFalse(user_exists)

class PrivateUserApiTests(TestCase):
    @classmethod
    def setUpTestData(cls):
        cls.payload ={
            'phonenumber':'09101010101',
            'password':'testpass123',
            'first_name':'Test Name',
            'last_name': 'Test Surname'
        }
        cls.user = create_user(**cls.payload)

    def setUp(self):
        super().setUp()
        self.client = APIClient()

        # Obtain JWT access token
        token_response = self.client.post(
            reverse('Accounts:login'),
            data={'phonenumber': '09101010101', 'password': 'testpass123'},
            format='json'
        )
        self.assertEqual(token_response.status_code, status.HTTP_200_OK)
        self.access = token_response.data['access']

    def test_unauthenticated_user_cant_access_user_detail_endpoint(self):
        response = self.client.get(reverse('Accounts:me'))
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_can_see_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.get(reverse('Accounts:me'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)

    def test_authenticated_user_retrieves_correct_info(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.get(reverse('Accounts:me'))
        self.assertEqual(response.data['phonenumber'], '09101010101')
        self.assertEqual(response.data['first_name'], 'Test Name')

    def test_unauthenticated_user_cant_edit_user_detail(self):
        response = self.client.put(reverse('Accounts:me'), data= self.payload)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
    
    def test_authenticated_user_can_edit_user_detail(self):
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {self.access}")
        response = self.client.patch(
            reverse('Accounts:me'),
            data={
                'phonenumber': '09101010101',
                'password' : 'alteredPass123',
                'email' : 'test@example.com',
                'first_name': 'New Name',
                'last_name': 'New last name'
            },
            format = 'json'
            )
        
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        self.user.refresh_from_db()
        self.assertEqual(self.user.phonenumber, '09101010101')
        self.assertTrue(self.user.check_password('alteredPass123'))
        self.assertEqual(self.user.email, 'test@example.com')
        self.assertEqual(self.user.first_name, 'New Name')
        self.assertEqual(self.user.last_name, 'New last name')

