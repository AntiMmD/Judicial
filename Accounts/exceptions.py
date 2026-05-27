from rest_framework.exceptions import APIException
from rest_framework import status

class RateLimitExceeded(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً دوباره تلاش کنید.'
    default_code = 'too_many_requests'

class TooManyAttemptsError(APIException):
    status_code = status.HTTP_429_TOO_MANY_REQUESTS
    default_detail = 'درخواست‌های شما بیش از حد مجاز است. لطفاً بعداً دوباره تلاش کنید.'
    default_code = 'too_many_requests'
    
class InvalidOTPError(APIException):
    status_code = status.HTTP_401_UNAUTHORIZED
    default_detail = 'کد یکبار مصرف وارد شده درست نیست.'
    default_code = 'invalid_otp'
