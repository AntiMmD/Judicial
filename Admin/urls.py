from django.urls import path
from Accounts.api import views
from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

urlpatterns = [
    # path('users/', views.CreateUserView.as_view(), name='create'),
    # path('users/', views.CreateUserView.as_view(), name='create'),
    # path('auth/request-otp/', views.RequestOTPView.as_view() , name='request-otp'),
    # path('auth/verify-otp/', views.VerifyOTPView.as_view() , name='verify-otp'),
    # path('auth/token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    # path('auth/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),

    path('users/<int:pk>/', views.UserDetailViewForUser.as_view(), name='manage-user'),
    path('users/', views.UserDetailViewForAdmins.as_view(), name='users-list'),
    path('me/', views.UserDetailViewForUser.as_view() , name='me'),
    path('request-otp/', views.RequestOTPView.as_view() , name='request-otp'),
    path('verify-otp/', views.VerifyOTPView.as_view() , name='verify-otp'),
    path('login/', TokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]