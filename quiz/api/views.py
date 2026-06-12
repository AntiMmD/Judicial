from django.shortcuts import get_object_or_404
from django.utils import timezone
from math import ceil
from rest_framework import generics, status
from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample

from ..models import (
    Quiz,
    QuizAttempt,
    Question,
    Answer,
    Option,
    QuizPayment
)

from .serializers import (
    QuestionSerializer,
    SubmitAnswerSerializer,
    QuizResultSerializer,
    LeaderboardSerializer,
    QuizCreateSerializer,
    QuizDetailSerializer,
)


def get_remaining_seconds(attempt):
    end_time = attempt.start_time + timezone.timedelta(
        minutes=attempt.quiz.duration
    )

    remaining = (end_time - timezone.now()).total_seconds()

    return max(0, int(remaining))


def auto_finish(attempt):

    if attempt.finished:
        return

    if get_remaining_seconds(attempt) > 0:
        return

    total_score = 0

    answers = attempt.answers.select_related(
        "question",
        "selected_option"
    )

    for answer in answers:
        if answer.selected_option and answer.selected_option.is_correct:
            total_score += answer.question.score

    attempt.score = total_score
    attempt.finished = True
    attempt.save()


class QuizListCreateAPIView(generics.ListCreateAPIView):
    permission_classes = [AllowAny]
    queryset = Quiz.objects.prefetch_related("questions__options").order_by("-created_at")

    def get_serializer_class(self):
        if self.request.method == "POST":
            return QuizCreateSerializer
        return QuizDetailSerializer

    @extend_schema(
        request=QuizCreateSerializer,
        responses={201: QuizDetailSerializer},
        examples=[
            OpenApiExample(
                "Create quiz request",
                value={
                    "title": "آزمون حقوق مدنی",
                    "description": "آزمون پایان ترم",
                    "start_time": "2026-06-15T10:00:00+03:30",
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
                },
                request_only=True,
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        quiz = serializer.save()
        return Response(
            QuizDetailSerializer(quiz).data,
            status=status.HTTP_201_CREATED,
        )


class StartQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, quiz_id):

        quiz = get_object_or_404(
            Quiz,
            id=quiz_id,
            is_active=True
        )

        now = timezone.now()

        if now < quiz.start_time:
            return Response(
                {"detail": "آزمون هنوز شروع نشده است"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if now > quiz.end_time():
            return Response(
                {"detail": "زمان آزمون به پایان رسیده"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if quiz.price > 0:

            paid = QuizPayment.objects.filter(
                user=request.user,
                quiz=quiz,
                paid=True
            ).exists()

            if not paid:
                return Response(
                    {"detail": "برای شرکت در این آزمون باید پرداخت انجام دهید"},
                    status=status.HTTP_402_PAYMENT_REQUIRED
                )

        attempt = QuizAttempt.objects.filter(
            user=request.user,
            quiz=quiz
        ).first()

        if attempt:

            if attempt.finished:
                return Response(
                    {"detail": "قبلاً در آزمون شرکت کرده‌اید"},
                    status=status.HTTP_400_BAD_REQUEST
                )

            return Response({
                "attempt_id": attempt.id,
                "remaining_seconds": get_remaining_seconds(attempt),
                "resume": True
            })

        attempt = QuizAttempt.objects.create(
            user=request.user,
            quiz=quiz
        )


        total_questions = quiz.questions.count()
        per_page = 1
        total_pages = ceil(total_questions / per_page)

        return Response({
            "attempt_id": attempt.id,
            "remaining_seconds": get_remaining_seconds(attempt),
            "resume": False,
            "total_pages": total_pages
        })


class AttemptStatusAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):

        attempt = get_object_or_404(QuizAttempt, id=attempt_id)

        if attempt.user != request.user:
            return Response({"detail": "دسترسی غیر مجاز"}, status=status.HTTP_403_FORBIDDEN)

        auto_finish(attempt)

        return Response({
            "remaining_seconds": get_remaining_seconds(attempt),
            "finished": attempt.finished
        })


class GetQuestionAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):

        quiz = get_object_or_404(Quiz, id=quiz_id)

        attempt = get_object_or_404(
            QuizAttempt,
            quiz=quiz,
            user=request.user
        )

        if attempt.user != request.user:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        auto_finish(attempt)

        if attempt.finished:
            return Response(
                {"detail": "آزمون پایان یافته"},
                status=status.HTTP_400_BAD_REQUEST
            )

        page = int(request.GET.get("page", 1))
        per_page = 1

        questions = quiz.questions.all()

        if request.GET.get("shuffle") == "1":
            questions = questions.order_by("?")
        else:
            questions = questions.order_by("order")

        start = (page - 1) * per_page
        end = start + per_page

        question = questions[start:end].first()

        if not question:
            return Response(
                {"detail": "سوالی وجود ندارد"},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = QuestionSerializer(
            question,
            context={"request": request}
        )

        existing_answer = Answer.objects.filter(
            attempt=attempt,
            question=question,
        ).first()

        return Response({
            "question": serializer.data,
            "remaining_seconds": get_remaining_seconds(attempt),
            "page": page,
            "selected_option_id": (
                existing_answer.selected_option_id if existing_answer else None
            ),
        })


class SubmitAnswerAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):

        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id
        )

        if attempt.user != request.user:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        auto_finish(attempt)

        if attempt.finished:
            return Response(
                {"detail": "آزمون پایان یافته"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = SubmitAnswerSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        question = serializer.validated_data["question"]
        option = serializer.validated_data["selected_option"]

        if question.quiz != attempt.quiz:
            return Response(
                {"detail": "سوال نامعتبر"},
                status=status.HTTP_400_BAD_REQUEST
            )

        if option.question != question:
            return Response(
                {"detail": "گزینه نامعتبر"},
                status=status.HTTP_400_BAD_REQUEST
            )

        Answer.objects.update_or_create(
            attempt=attempt,
            question=question,
            defaults={
                "selected_option": option
            }
        )

        return Response({
            "detail": "پاسخ ثبت شد",
            "remaining_seconds": get_remaining_seconds(attempt)
        })


class FinishQuizAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, attempt_id):

        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id
        )

        if attempt.user != request.user:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        if attempt.finished:
            return Response(
                {"detail": "قبلاً پایان یافته"},
                status=status.HTTP_400_BAD_REQUEST
            )

        total_score = 0

        answers = attempt.answers.select_related(
            "question",
            "selected_option"
        )

        for answer in answers:

            if answer.selected_option and answer.selected_option.is_correct:
                total_score += answer.question.score

        attempt.score = total_score
        attempt.finished = True
        attempt.save()

        return Response({
            "score": total_score,
            "detail": "آزمون پایان یافت"
        })


class QuizResultAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, attempt_id):

        attempt = get_object_or_404(
            QuizAttempt,
            id=attempt_id
        )

        if attempt.user != request.user:
            return Response({"detail": "Unauthorized"}, status=status.HTTP_403_FORBIDDEN)

        auto_finish(attempt)

        if not attempt.finished:
            return Response(
                {"detail": "آزمون هنوز پایان نیافته"},
                status=status.HTTP_400_BAD_REQUEST
            )

        serializer = QuizResultSerializer(attempt)

        return Response(serializer.data)


class LeaderboardAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, quiz_id):

        attempts = QuizAttempt.objects.filter(
            quiz_id=quiz_id,
            finished=True
        ).select_related("user").order_by("-score")[:50]

        serializer = LeaderboardSerializer(
            attempts,
            many=True
        )

        return Response(serializer.data)
