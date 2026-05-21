import secrets
import redis
from rest_framework_simplejwt.tokens import RefreshToken

redis_client = redis.Redis(
    host='redis',
    port=6379,
    db=0,
    decode_responses=True
)

def generate_otp():
    return f"{secrets.randbelow(10**6):06d}"

def save_otp(phonenumber, otp):
    redis_client.setex(
        f"otp:{phonenumber}",
        120,
        otp
    )

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
