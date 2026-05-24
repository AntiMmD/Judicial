from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status
from job.models import Job

JOB_LIST_URL = reverse('job:job-list')

User = get_user_model()


def create_user(**params):
    return User.objects.create_user(**params)

def create_superuser(**params):
    user = create_user(**params)
    user.is_staff = True
    user.is_superuser = True
    user.save()
    return user

def get_access_token(user):
    from rest_framework_simplejwt.tokens import RefreshToken
    refresh = RefreshToken.for_user(user)
    return str(refresh.access_token)



class PublicJobApiTests(TestCase):
    pass

class PrivateJobApiTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.adminPass = "adminpass123"
        cls.userPass = "testpass123"
        cls.admin = create_superuser(
            phonenumber="09123456789", password= cls.adminPass , first_name="Admin"
        )
        cls.user = create_user(
            phonenumber="09101010101",
            password= cls.userPass,
            first_name="Test Name",
            last_name="Test Surname",
        )
        cls.job = Job.objects.create(
            occupation="Engineer", description="text", is_active=True
        )

        cls.job_data = {
            "occupation": "Doctor",
            "description": "text",
            "is_active": True,
        }

        cls.MANAGE_JOB_URL = reverse('job:manage-job', args=[cls.job.id])

    def setUp(self):
        self.client = APIClient()

    def login(self, user):
        access = get_access_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_unauthenticated_user_cannot_create_job(self):
        response = self.client.post(JOB_LIST_URL, data= self.job_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_create_job(self):
        self.login(self.user)
        response = self.client.post(JOB_LIST_URL, data= self.job_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_only_admin_can_create_job(self):
        self.login(self.admin)
        response = self.client.post(JOB_LIST_URL, data= self.job_data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

    def test_unauthenticated_user_cannot_manage_job(self):
        self.assertEqual(
            self.client.get(self.MANAGE_JOB_URL).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )
        self.assertEqual(
            self.client.put(self.MANAGE_JOB_URL).status_code,
            status.HTTP_401_UNAUTHORIZED,
        )

    def test_authenticated_user_cannot_manage_job(self):
        self.login(self.user)
        self.assertEqual(
            self.client.get(self.MANAGE_JOB_URL).status_code,
            status.HTTP_403_FORBIDDEN,
        )
        self.assertEqual(
            self.client.patch(self.MANAGE_JOB_URL, self.job_data, format="json").status_code,
            status.HTTP_403_FORBIDDEN,
        )

    def test_only_admin_can_manage_job(self):
        self.login(self.admin)

        update_data = {
            "occupation": "mechanic",
            "description": "description",
            "is_active": False,
        }
        response = self.client.patch(self.MANAGE_JOB_URL, update_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['occupation'], "mechanic")
        self.assertEqual(response.data['description'], "description")
        self.assertEqual(response.data['is_active'], False)

    def test_unauthenticated_user_cannot_view_job_list(self):
        response = self.client.get(JOB_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_view_job_list(self):
        self.login(self.user)
        response = self.client.get(JOB_LIST_URL)
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_view_job_list(self):
        self.login(self.admin)

        Job.objects.create(occupation="Teacher", description="text", is_active=True)
        Job.objects.create(occupation="Nurse", description="text", is_active=True)

        response = self.client.get(JOB_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), Job.objects.count())