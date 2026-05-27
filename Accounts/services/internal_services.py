import secrets
import redis

from rest_framework_simplejwt.tokens import RefreshToken

from Accounts.exceptions import (
    RateLimitExceeded,
    InvalidOTPError,

)

redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)

def _check_rate_limit(phonenumber, limit=1, window=120):
    """
    Checks if the user has exceeded the OTP request limit.
    limit: Max number of requests allowed.
    window: Time window in seconds.
    """
    key = f"rate_limit:otp:{phonenumber}"
    
    # Get current count
    count = redis_client.get(key)
    
    if count and int(count) >= limit:
        raise RateLimitExceeded
    
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    if not count:  # Set expiration only on the first request in the window
        pipeline.expire(key, window)
    pipeline.execute()
    
    return True

def _save_otp(phonenumber, otp):
    redis_client.setex(
        name=f"otp:{phonenumber}",
        time=120,
        value=otp
    )


def _generate_otp():
    return f"{secrets.randbelow(10**6):06d}"


def generate_and_save_otp(phonenumber):
    if not _check_rate_limit(phonenumber):
        raise RateLimitExceeded()

    otp = _generate_otp()
    _save_otp(phonenumber, otp)
    return otp


def _check_retry_attempts(phonenumber, allowed_retry_attempts):
    retry_key = f"retry_attempts:otp:{phonenumber}"

    raw_val = redis_client.get(retry_key)
    if not raw_val:
        redis_client.setex(name=retry_key,time=120, value='1')
        return retry_key
    
    retry_attempts = int(raw_val)
    if not retry_attempts or retry_attempts < allowed_retry_attempts:
        redis_client.incr(retry_key)
        return retry_key
    
    raise RateLimitExceeded()
    

def verify_otp(phonenumber, otp:str, allowed_retry_attempts: int= 3):
    retry_key= _check_retry_attempts(phonenumber, allowed_retry_attempts)
    saved= redis_client.get(f"otp:{phonenumber}")

    if saved is None:
        raise InvalidOTPError()

    if saved == otp:
        redis_client.delete(f"otp:{phonenumber}")
        redis_client.delete(retry_key)
        return True

    raise InvalidOTPError()

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
