from django.urls import path
from .views import RegistrationView, EmailVerificationView, CustomTokenObtainPairView, ProfileView, ProfileDeleteView
from rest_framework_simplejwt.views import TokenRefreshView

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('email-verification/<str:code>/', EmailVerificationView.as_view(), name='email_verification'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
]
