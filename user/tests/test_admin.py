from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import Client

class AdminSiteTest(TestCase):
    
    def setUp(self):
        self.client = Client()
        self.admin_user = get_user_model().objects.create_superuser(
            phonenumber = '12345678911',
            email = 'admin@exmaple.com',
            password = 'testpass123',
        )
        self.client.force_login(self.admin_user)

        self.user = get_user_model().objects.create_user(
            phonenumber = '11987654321',
            email = 'user@example.com',
            password='testpass1234',
            name = 'Test User'
        )

    def test_user_list(self):
        url = reverse('admin:user_user_changelist')
        response = self.client.get(url)

        self.assertContains(response, self.user.name)
        self.assertContains(response, self.user.phonenumber)
        self.assertContains(response, self.user.email)

    def test_edit_user_page(self):
        # reverse('admin:appName_user_change')
        url = reverse('admin:user_user_change', args=[self.user.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)
    
    def test_create_user_page(self):
        url = reverse('admin:user_user_add')
        response = self.client.get(url)

        self.assertEqual(response.status_code, 200)