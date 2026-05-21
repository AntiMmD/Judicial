from django.contrib import admin
from django.forms.models import BaseInlineFormSet
from django.core.exceptions import ValidationError
from django.templatetags.static import static

from nested_admin import NestedModelAdmin, NestedStackedInline

from .models import Quiz, Question, Option, QuizAttempt, QuizResult, QuizPayment , Answer


class OptionInlineFormSet(BaseInlineFormSet):
    def clean(self):
        super().clean()

        correct_options_count = sum(
            1 for form in self.forms
            if form.cleaned_data.get('is_correct') and not form.cleaned_data.get('DELETE', False)
        )

        if correct_options_count == 0:
            raise ValidationError('حداقل یک گزینه باید صحیح باشد.')

        if correct_options_count > 1:
            raise ValidationError('فقط یک گزینه می‌تواند صحیح باشد.')


class OptionInline(NestedStackedInline):
    model = Option
    fields = ['text', 'is_correct']
    extra = 0

    formset = OptionInlineFormSet


class QuestionInline(NestedStackedInline):
    model = Question
    fields = ['text', 'order', 'score']
    extra = 0

    inlines = [OptionInline]


@admin.register(Quiz)
class QuizAdmin(NestedModelAdmin):

    list_display = [
        'title',
        'start_time',
        'duration',
        'price',
        'is_active'
    ]

    search_fields = ['title']

    list_filter = [
        'is_active',
        'start_time'
    ]

    inlines = [QuestionInline]



    class Media:
        css = {
            'all': (static('assets/css/nested-input.css'),)
        }

@admin.register(QuizPayment)
class QuizPaymentAdmin(admin.ModelAdmin):

    list_display = [
        'user',
        'quiz',
        'amount',
        'paid',
        'payment_key',
        'created_at'
    ]

    search_fields = [
        'payment_key',
        'user__phonenumber'
    ]

    list_filter = [
        'paid'
    ]

    autocomplete_fields = [
        'user',
        'quiz'
    ]

from django.urls import reverse
from django.utils.html import format_html


class QuizAttemptInline(admin.TabularInline):

    model = QuizAttempt

    fields = [
        "user",
        "score",
        "finished",
        "start_time",
        "view_answers"
    ]

    readonly_fields = fields

    extra = 0

    def view_answers(self, obj):
        url = reverse("admin:quiz_quizattempt_change", args=[obj.id])
        return format_html('<a href="{}">مشاهده</a>', url)

    view_answers.short_description = "پاسخ‌ها"


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):

    list_display = [
        "title",
        "start_time",
        "attempt_count"
    ]

    search_fields = [
        "title"
    ]

    inlines = [
        QuizAttemptInline
    ]

    def attempt_count(self, obj):
        return obj.attempts.count()

    attempt_count.short_description = "تعداد شرکت‌کنندگان"

class AnswerInline(admin.TabularInline):

    model = Answer

    fields = [
        "question",
        "selected_option",
    ]

    readonly_fields = [
        "question",
        "selected_option",
    ]

    extra = 0

@admin.register(QuizAttempt)
class QuizAttemptAdmin(admin.ModelAdmin):

    list_display = [
        "user",
        "quiz",
        "score",
        "finished",
        "start_time"
    ]

    search_fields = [
        "user__phonenumber",
        "user__username"
    ]

    list_filter = [
        "quiz",
        "finished"
    ]

    readonly_fields = [
        "user",
        "quiz",
        "score",
        "start_time",
        "finished"
    ]

    inlines = [
        AnswerInline
    ]

    def has_module_permission(self, request):
        return False