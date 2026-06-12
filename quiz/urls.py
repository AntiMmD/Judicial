from django.urls import path

from .api.views import (
    QuizListCreateAPIView,
    StartQuizAPIView,
    AttemptStatusAPIView,
    GetQuestionAPIView,
    SubmitAnswerAPIView,
    FinishQuizAPIView,
    QuizResultAPIView,
)

urlpatterns = [
    path("", QuizListCreateAPIView.as_view(), name="quiz-list-create"),
    # Quiz start
    path("start/<int:quiz_id>/",StartQuizAPIView.as_view(),name="quiz-start"),
    # Get questions
    path("question/<int:quiz_id>/",GetQuestionAPIView.as_view(),name="quiz-question"),
    # Quiz status (Timer)
    path("attempt-status/<int:attempt_id>/",AttemptStatusAPIView.as_view(),name="attempt-status"),
    # Set answers
    path("attempt-answer/<int:attempt_id>/",SubmitAnswerAPIView.as_view(),name="submit-answer"),
    # Quiz end
    path("attempt-finish/<int:attempt_id>/",FinishQuizAPIView.as_view(),name="finish-quiz"),
    # Quiz result
    path("attempt-result/<int:attempt_id>/",QuizResultAPIView.as_view(),name="quiz-result"),
]
