from django.db import transaction
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


class AnswerDetailSerializer(serializers.Serializer):
    question = serializers.CharField()
    selected_option = serializers.CharField(allow_null=True)
    correct_option = serializers.CharField()
    is_correct = serializers.BooleanField()


class QuizResultSerializer(serializers.ModelSerializer):

    quiz = serializers.CharField(source="quiz.title")
    answers = serializers.SerializerMethodField()

    class Meta:
        model = QuizAttempt
        fields = [
            "id",
            "quiz",
            "score",
            "finished",
            "answers",
        ]

    def get_answers(self, obj):
        questions = (
            obj.quiz.questions.prefetch_related("options")
            .order_by("order")
        )
        user_answers = {
            answer.question_id: answer
            for answer in obj.answers.select_related("selected_option").all()
        }

        results = []
        for question in questions:
            answer = user_answers.get(question.id)
            selected = answer.selected_option if answer else None
            correct = question.options.filter(is_correct=True).first()

            results.append({
                "question": question.text,
                "selected_option": selected.text if selected else None,
                "correct_option": correct.text if correct else "",
                "is_correct": bool(selected and selected.is_correct),
            })

        return results


class LeaderboardSerializer(serializers.ModelSerializer):

    username = serializers.CharField(source="user.username")

    class Meta:
        model = QuizAttempt
        fields = [
            "username",
            "score"
        ]


class OptionCreateSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ["text", "is_correct"]


class QuestionCreateSerializer(serializers.ModelSerializer):

    options = OptionCreateSerializer(many=True)

    class Meta:
        model = Question
        fields = ["text", "order", "score", "options"]

    def validate_options(self, value):
        if not value:
            raise serializers.ValidationError(
                "هر سوال باید حداقل یک گزینه داشته باشد."
            )

        correct_count = sum(1 for option in value if option.get("is_correct"))

        if correct_count == 0:
            raise serializers.ValidationError("حداقل یک گزینه باید صحیح باشد.")

        if correct_count > 1:
            raise serializers.ValidationError("فقط یک گزینه می‌تواند صحیح باشد.")

        return value


class QuizCreateSerializer(serializers.ModelSerializer):

    questions = QuestionCreateSerializer(many=True)

    class Meta:
        model = Quiz
        fields = [
            "title",
            "description",
            "start_time",
            "duration",
            "price",
            "is_active",
            "questions",
        ]

    def validate_questions(self, value):
        if not value:
            raise serializers.ValidationError(
                "آزمون باید حداقل یک سوال داشته باشد."
            )
        return value

    @transaction.atomic
    def create(self, validated_data):
        questions_data = validated_data.pop("questions")
        quiz = Quiz.objects.create(**validated_data)

        for question_data in questions_data:
            options_data = question_data.pop("options")
            question = Question.objects.create(quiz=quiz, **question_data)

            for option_data in options_data:
                Option.objects.create(question=question, **option_data)

        return quiz


class OptionDetailSerializer(serializers.ModelSerializer):

    class Meta:
        model = Option
        fields = ["id", "text", "is_correct"]


class QuestionDetailSerializer(serializers.ModelSerializer):

    options = OptionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Question
        fields = ["id", "text", "order", "score", "options"]


class QuizDetailSerializer(serializers.ModelSerializer):

    questions = QuestionDetailSerializer(many=True, read_only=True)

    class Meta:
        model = Quiz
        fields = [
            "id",
            "title",
            "description",
            "start_time",
            "duration",
            "price",
            "is_active",
            "created_at",
            "questions",
        ]
