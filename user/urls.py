from django.urls import path
from user.api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

app_name = 'user'

urlpatterns = [
    # path('users/', views.CreateUserView.as_view(), name='create'),
    # path('users/', views.CreateUserView.as_view(), name='create'),
    # path('me/', views.ManageUserView.as_view() , name='me'),
    # path('auth/request-otp/', views.RequestOTPView.as_view() , name='request-otp'),
    # path('auth/verify-otp/', views.VerifyOTPView.as_view() , name='verify-otp'),
    # path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<int:pk>/', views.UserDetailView.as_view(), name='manage-user'),
    path('users/', views.UserListCreateView.as_view(), name='users-list'),
    path('request-otp/', views.RequestOTPView.as_view() , name='request-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view() , name='verify-otp'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]