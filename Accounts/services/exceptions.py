from rest_framework.exceptions import APIException
from rest_framework import status

class RateLimitExceeded(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً دوباره تلاش کنید.'
    default_code = 'too_many_requests'