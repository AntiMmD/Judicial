from django.apps import AppConfig


<<<<<<<< HEAD:quiz/apps.py
class QuizConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'quiz'
    verbose_name = 'آزمون'
========
class DocumentsConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'Documents'
>>>>>>>> e50608e8b6819f99187957da6adfc3cdcb7249fe:Documents/apps.py
