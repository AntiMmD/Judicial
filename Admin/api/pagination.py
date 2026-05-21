from django.contrib.auth import get_user_model
from rest_framework.pagination import PageNumberPagination
from rest_framework import serializers

User = get_user_model()


class UserPagination(PageNumberPagination):
    page_size = 30
    page_size_query_param = "page_size"
    max_page_size = 100