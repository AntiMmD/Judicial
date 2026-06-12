from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.utils import timezone
from datetime import timedelta
from rest_framework.test import APIClient
from rest_framework import status

from quiz.models import Quiz

QUIZ_LIST_URL = reverse("quiz-list-create")

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


class QuizCreateApiTests(TestCase):

    @classmethod
    def setUpTestData(cls):
        cls.admin_pass = "adminpass123"
        cls.user_pass = "testpass123"
        cls.admin = create_superuser(
            phonenumber="09123456789",
            password=cls.admin_pass,
            first_name="Admin",
        )
        cls.user = create_user(
            phonenumber="09101010101",
            password=cls.user_pass,
            first_name="Test",
            last_name="User",
        )
        cls.quiz_data = {
            "title": "آزمون حقوق مدنی",
            "description": "آزمون پایان ترم",
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "duration": 45,
            "price": 0,
            "is_active": True,
            "questions": [
                {
                    "text": "کدام ماده مربوط به قرارداد است؟",
                    "order": 1,
                    "score": 2,
                    "options": [
                        {"text": "ماده ۱۰", "is_correct": True},
                        {"text": "ماده ۲۰", "is_correct": False},
                    ],
                }
            ],
        }

    def setUp(self):
        self.client = APIClient()

    def login(self, user):
        access = get_access_token(user)
        self.client.credentials(HTTP_AUTHORIZATION=f"Bearer {access}")

    def test_unauthenticated_user_cannot_create_quiz(self):
        response = self.client.post(QUIZ_LIST_URL, self.quiz_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    def test_authenticated_user_cannot_create_quiz(self):
        self.login(self.user)
        response = self.client.post(QUIZ_LIST_URL, self.quiz_data, format="json")
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)

    def test_admin_can_create_quiz(self):
        self.login(self.admin)
        response = self.client.post(QUIZ_LIST_URL, self.quiz_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Quiz.objects.count(), 1)

        quiz = Quiz.objects.first()
        self.assertEqual(quiz.title, self.quiz_data["title"])
        self.assertEqual(quiz.questions.count(), 1)
        self.assertEqual(quiz.questions.first().options.count(), 2)
        self.assertEqual(response.data["id"], quiz.id)
        self.assertEqual(len(response.data["questions"]), 1)

    def test_create_quiz_requires_at_least_one_question(self):
        self.login(self.admin)
        invalid_data = {**self.quiz_data, "questions": []}

        response = self.client.post(QUIZ_LIST_URL, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 0)

    def test_create_quiz_requires_exactly_one_correct_option(self):
        self.login(self.admin)
        invalid_data = {
            **self.quiz_data,
            "questions": [
                {
                    "text": "سوال تست",
                    "order": 1,
                    "score": 1,
                    "options": [
                        {"text": "گزینه ۱", "is_correct": True},
                        {"text": "گزینه ۲", "is_correct": True},
                    ],
                }
            ],
        }

        response = self.client.post(QUIZ_LIST_URL, invalid_data, format="json")

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertEqual(Quiz.objects.count(), 0)

    def test_admin_can_list_quizzes(self):
        self.login(self.admin)
        self.client.post(QUIZ_LIST_URL, self.quiz_data, format="json")

        response = self.client.get(QUIZ_LIST_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
