# from django.test import TestCase
# from django.contrib.auth import get_user_model
# from django.urls import reverse

# from rest_framework.test import APIClient
# from rest_framework import status

# User = get_user_model()
# CREATE_USER_URL = reverse('Accounts:users-list')

# def create_user(**params):
#     return User.objects.create_user(**params)

# class PublicUserApiTests(TestCase):

#     def setUp(self):
#         self.client = APIClient()
    
#     def test_create_user_successful(self):
#         payload ={
#             'phonenumber':'09101010101',
#             'password':'testpass1234',
#             'first_name':'Test Name',
#             'last_name': 'Test Surname'
#         }
#         response = self.client.post(CREATE_USER_URL, payload)

#         self.assertEqual(response.status_code, status.HTTP_201_CREATED)

#         user = User.objects.get(phonenumber = payload['phonenumber'])
#         self.assertTrue(user.check_password(payload['password']))
#         self.assertNotIn('password',response.data)

#     def test_user_with_phonenumber_exists_error(self):
#         payload ={
#             'phonenumber':'09101010101',
#             'password':'testpass1234',
#             'first_name':'Test Name',
#             'last_name': 'Test Surname',
#         }
#         create_user(**payload)
#         response = self.client.post(CREATE_USER_URL, payload)

#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

#     def test_password_too_short_error(self):
#         payload ={
#             'phonenumber':'09101010101',
#             'password':'p23',
#             'first_name':'Test Name',
#             'last_name': 'Test Surname',            
#         }
#         response = self.client.post(CREATE_USER_URL, payload)
#         self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
#         user_exists = User.objects.filter(phonenumber = payload['phonenumber']).exists()
#         self.assertFalse(user_exists)