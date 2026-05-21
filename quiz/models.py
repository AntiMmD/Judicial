from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta


class Quiz(models.Model):
    title = models.CharField(max_length=255, verbose_name="نام آزمون")
    description = models.TextField(blank=True, verbose_name="توضیحات")

    start_time = models.DateTimeField(verbose_name="زمان شروع آزمون")
    duration = models.PositiveIntegerField(default=30, verbose_name="مدت آزمون (دقیقه)")

    price = models.PositiveBigIntegerField(default=0, verbose_name="قیمت آزمون", help_text="ریال")

    is_active = models.BooleanField(default=True , verbose_name='آزمون فعال است؟')

    created_at = models.DateTimeField(auto_now_add=True , verbose_name='ثبت شده در')

    def end_time(self):
        return self.start_time + timedelta(minutes=self.duration)

    def is_running(self):
        now = timezone.now()
        return self.start_time <= now <= self.end_time()

    def __str__(self):
        return self.title
    
    class Meta:
        verbose_name = "آزمون"
        verbose_name_plural = "آزمون‌ها"

class Question(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="questions",
        verbose_name="آزمون"
    )

    text = models.TextField(verbose_name="متن سوال")

    order = models.PositiveIntegerField(default=1, verbose_name="ترتیب سوال")

    score = models.PositiveIntegerField(default=1, verbose_name="نمره سوال")

    def __str__(self):
        return f"{self.quiz.title} - سوال {self.order}"
    
    class Meta:
        verbose_name = 'سوال'
        verbose_name_plural = 'سوالات'

class Option(models.Model):

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        related_name="options",
    )

    text = models.CharField(max_length=500, verbose_name='متن گزینه',)

    is_correct = models.BooleanField(default=False, verbose_name='ایا این گزینه صحیح است؟')

    def __str__(self):
        return self.text
    
    class Meta:
        verbose_name = 'گزینه'
        verbose_name_plural = 'گزینه ها'

class QuizAttempt(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_attempts",
        verbose_name='کاربر'
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="attempts",
        verbose_name='آزمون'
    )

    start_time = models.DateTimeField(default=timezone.now , verbose_name='تاریخ شروع' )

    finished = models.BooleanField(default=False , verbose_name='تمام شده')

    score = models.FloatField(default=0 , verbose_name='نمره')

    created_at = models.DateTimeField(auto_now_add=True , verbose_name='ثبت شده در')

    class Meta:
        unique_together = ["user", "quiz"]
        verbose_name = "شرکت در آزمون"
        verbose_name_plural = "شرکت‌های کاربران در آزمون"

    def __str__(self):
        return f"{self.user} - {self.quiz}"

class Answer(models.Model):

    attempt = models.ForeignKey(
        QuizAttempt,
        on_delete=models.CASCADE,
        related_name="answers",
        verbose_name='شرکت در آزمون'
    )

    question = models.ForeignKey(
        Question,
        on_delete=models.CASCADE,
        verbose_name='سوال'
    )

    selected_option = models.ForeignKey(
        Option,
        on_delete=models.CASCADE,
        null=True,
        blank=True,
        verbose_name='پاسخ کاربر'
    )

    def is_correct(self):
        return self.selected_option and self.selected_option.is_correct
    
    class Meta:
        verbose_name = "پاسخ کاربر"
        verbose_name_plural = "پاسخ‌های کاربران"

class QuizPayment(models.Model):

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name='کاربر'
    )

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="payments",
        verbose_name='آزمون'
    )

    amount = models.PositiveBigIntegerField(
        verbose_name="مبلغ"
    )

    paid = models.BooleanField(
        default=False,
        verbose_name="پرداخت شده"
    )

    payment_key = models.CharField(
        max_length=150,
        verbose_name="کد پرداخت"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )


    def __str__(self):
        return f"{self.user} - {self.quiz}"
    
    class Meta:
        verbose_name = "پرداخت آزمون"
        verbose_name_plural = "پرداخت‌های آزمون"


class QuizLeaderboard(models.Model):

    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="leaderboard",
        verbose_name="آزمون"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        verbose_name="کاربر"
    )

    score = models.FloatField(
        verbose_name="نمره"
    )

    rank = models.PositiveIntegerField(
        verbose_name="رتبه"
    )


    class Meta:
        ordering = ["rank"]


class QuizResult(Quiz):

    class Meta:
        proxy = True
        verbose_name = "نتیجه آزمون"
        verbose_name_plural = "نتایج آزمون‌ها"
