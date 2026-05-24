import secrets
import redis
from rest_framework_simplejwt.tokens import RefreshToken

from Accounts.services.exceptions import RateLimitExceeded

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
        return False  # Rate limit exceeded
    
    
    pipeline = redis_client.pipeline()
    pipeline.incr(key)
    if not count:  # Set expiration only on the first request in the window
        pipeline.expire(key, window)
    pipeline.execute()
    
    return True

def _save_otp(phonenumber, otp):
    redis_client.setex(
        f"otp:{phonenumber}",
        120,
        otp
    )


def _generate_otp():
    return f"{secrets.randbelow(10**6):06d}"


def generate_and_save_otp(phonenumber):
    if not _check_rate_limit(phonenumber):
        raise RateLimitExceeded()

    otp = _generate_otp()
    _save_otp(phonenumber, otp)
    return otp


def verify_otp(phonenumber, otp):
    saved = redis_client.get(f"otp:{phonenumber}")

    if saved is None:
        return False

    if saved == otp:
        redis_client.delete(f"otp:{phonenumber}")
        return True

    return False

def get_tokens_for_user(user):
    refresh = RefreshToken.for_user(user)

    return {
        "refresh": str(refresh),
        "access": str(refresh.access_token),
    }
