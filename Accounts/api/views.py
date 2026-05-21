from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth import get_user_model

from Accounts.api.serializers import (
    UserSerializer,
    RequestOTPSerializer,
    VerifyOTPSerializer,
    TokenPairSerializer,
    MessageSerializer
)
from Accounts.services import internal_services, external_services
from Accounts.api.pagination import UserPagination

User = get_user_model()


class UserCreateViewForUser(generics.CreateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer
    pagination_class = UserPagination

    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        tokens = internal_services.get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)


class UserDetailViewForUser(generics.RetrieveUpdateAPIView):
    permission_classes = [AllowAny]
    queryset = User.objects.all()
    serializer_class = UserSerializer

    def get_object(self):
        return self.request.user
        
@extend_schema(
    request=RequestOTPSerializer,
    responses={200: MessageSerializer},
    examples=[
        OpenApiExample(
            "Request OTP",
            value={
                "phonenumber": "09123456789"
            },
            request_only=True,
        ),
        OpenApiExample(
            "OTP sent",
            value={
                "message": "OTP sent"
            },
            response_only=True,
            status_codes=["200"],
        ),
    ],
)
class RequestOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = RequestOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phonenumber = serializer.validated_data["phonenumber"]
        otp = internal_services.generate_otp()
        internal_services.save_otp(phonenumber, otp)
        external_services.send_sms(phonenumber, otp)

        return Response({"message": "OTP sent"}, status=status.HTTP_200_OK)


@extend_schema(
    request=VerifyOTPSerializer,
    responses={
        200: TokenPairSerializer,
        401: MessageSerializer
    },
    examples=[
        OpenApiExample(
            "Verify OTP request",
            value={
                "phonenumber": "09123456789",
                "otp": "123456"
            },
            request_only=True,
        ),
        OpenApiExample(
            "Successful authentication",
            value={
                "refresh": "token...",
                "access": "token..."
            },
            response_only=True,
            status_codes=["200"],
        ),
        OpenApiExample(
            "Invalid OTP",
            value={
                "message": "Invalid OTP"
            },
            response_only=True,
            status_codes=["401"],
        ),
    ],
)
class VerifyOTPView(generics.GenericAPIView):
    permission_classes = [AllowAny]
    serializer_class = VerifyOTPSerializer

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        phonenumber = serializer.validated_data["phonenumber"]
        otp = serializer.validated_data["otp"]

        if not internal_services.verify_otp(phonenumber, otp):
            return Response({"message": "Invalid OTP"}, status=status.HTTP_401_UNAUTHORIZED)

        user, _ = User.objects.get_or_create(phonenumber=phonenumber)
        tokens = internal_services.get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_200_OK)
