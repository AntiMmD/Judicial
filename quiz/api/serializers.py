from rest_framework import serializers
from ..models import (
    Quiz,
    Question,
    Option,
    QuizAttempt,
    Answer
)


class OptionSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = [
            "id",
            "text"
        ]


class QuestionSerializer(serializers.ModelSerializer):

    options = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = [
            "id",
            "text",
            "order",
            "options"
        ]

    def get_options(self, obj):
        request = self.context.get("request")

        options = obj.options.all()

        # options shuffle 
        if request and request.GET.get("shuffle") == "1":
            options = options.order_by("?")

        return OptionSerializer(options, many=True).data


class SubmitAnswerSerializer(serializers.Serializer):

    question = serializers.PrimaryKeyRelatedField(
        queryset=Question.objects.all()
    )

    selected_option = serializers.PrimaryKeyRelatedField(
        queryset=Option.objects.all()
    )


class AnswerDetailSerializer(serializers.ModelSerializer):

    question = serializers.CharField(source="question.text")
    selected_option = serializers.CharField(source="selected_option.text")

    class Meta:
        model = Answer
        fields = [
            "question",
            "selected_option"
        ]


class QuizResultSerializer(serializers.ModelSerializer):

    quiz = serializers.CharField(source="quiz.title")
    answers = AnswerDetailSerializer(many=True, read_only=True)

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "score",
            "finished",
            "answers"
        ]


class LeaderboardSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")

    class Meta:
        model = QuizAttempt
        fields = [
            "username",
            "score"
        ]
