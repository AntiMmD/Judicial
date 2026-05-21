from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated, IsAdminUser, AllowAny
from rest_framework.response import Response
from drf_spectacular.utils import extend_schema, OpenApiExample
from django.contrib.auth import get_user_model

from Admin.api.serializers import (
    UserSerializerForAdmins,
    TokenPairSerializer
)
from Admin.api.pagination import PageNumberPagination, UserPagination


User = get_user_model()

class UserDetailViewForAdmins(generics.RetrieveUpdateDestroyAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all()
    serializer_class = UserSerializerForAdmins


class UserListCreateView(generics.ListCreateAPIView):
    permission_classes = [IsAdminUser]
    queryset = User.objects.all().order_by("id")
    serializer_class = UserSerializerForAdmins
    pagination_class = UserPagination

    @extend_schema(
        request=UserSerializerForAdmins,
        responses={201: TokenPairSerializer},
        examples=[
            OpenApiExample(
                "Create user request",
                value={
                    "phonenumber": "09123456789",
                    "password": "strongpassword",
                    "first_name": "Ali",
                    "last_name": "Ahmadi",
                    "role": "admin",
                    "national_code": "1234567890",
                    "birthday_date": "1995-01-01",
                    "is_active": True,
                    "is_staff": True,
                },
                request_only=True,
            ),
            OpenApiExample(
                "Successful registration",
                value={
                    "refresh": "token...",
                    "access": "token..."
                },
                response_only=True,
                status_codes=["201"],
            ),
        ],
    )
    def post(self, request, *args, **kwargs):
        return self.create(request, *args, **kwargs)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = serializer.save()
        tokens = internal_services.get_tokens_for_user(user)
        return Response(tokens, status=status.HTTP_201_CREATED)