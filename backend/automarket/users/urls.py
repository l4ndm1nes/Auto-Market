from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView

from .views import (
    RegistrationView,
    EmailVerificationView,
    CustomTokenObtainPairView,
    ProfileView,
    ProfileDeleteView,
    AddToFavoriteView,
    RemoveFromFavoriteView
)

app_name = "users"

urlpatterns = [
    path('register/', RegistrationView.as_view(), name='register'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path(
        'email-verification/<str:code>/',
        EmailVerificationView.as_view(),
        name='email_verification'
    ),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('profile/delete/', ProfileDeleteView.as_view(), name='profile_delete'),
    path(
        'favorites/add/<int:car_listing_id>/',
        AddToFavoriteView.as_view(),
        name='add_to_favorite'
    ),
    path(
        'favorites/remove/<int:car_listing_id>/',
        RemoveFromFavoriteView.as_view(),
        name='remove_from_favorite'
    ),
]
