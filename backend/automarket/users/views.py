from rest_framework import status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView

from carlisting.models import CarListing
from .models import Favorite
from .serializers import (
    RegistrationSerializer,
    EmailVerificationSerializer,
    CustomTokenObtainPairSerializer,
    ProfileSerializer,
    ProfileDeleteSerializer,
)


class RegistrationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = RegistrationSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'User created successfully. Please verify your email.'},
                status=status.HTTP_201_CREATED
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class EmailVerificationView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, code):
        serializer = EmailVerificationSerializer(data={"code": code})
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'detail': 'Email verified successfully.'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer


class ProfileView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def get(self, request):
        serializer = ProfileSerializer(request.user)
        return Response(serializer.data)

    def post(self, request):
        serializer = ProfileSerializer(request.user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProfileDeleteView(APIView):
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        serializer = ProfileDeleteSerializer(data=request.data)
        if serializer.is_valid():
            user = request.user
            user.delete()
            return Response(
                {'detail': 'User deleted successfully.'},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddToFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_listing_id):
        try:
            car_listing = CarListing.objects.get(id=car_listing_id)
        except CarListing.DoesNotExist:
            return Response(
                {"detail": "Car listing not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        _, created = Favorite.objects.get_or_create(
            user=request.user,
            car_listing=car_listing
        )
        if created:
            return Response(
                {"detail": "Added to favorites."},
                status=status.HTTP_201_CREATED
            )
        return Response(
            {"detail": "Already in favorites."},
            status=status.HTTP_200_OK
        )


class RemoveFromFavoriteView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_listing_id):
        try:
            car_listing = CarListing.objects.get(id=car_listing_id)
        except CarListing.DoesNotExist:
            return Response(
                {"detail": "Car listing not found."},
                status=status.HTTP_404_NOT_FOUND
            )

        favorite = Favorite.objects.filter(user=request.user, car_listing=car_listing)
        if favorite.exists():
            favorite.delete()
            return Response(
                {"detail": "Removed from favorites."},
                status=status.HTTP_204_NO_CONTENT
            )
        return Response(
            {"detail": "Not in favorites."},
            status=status.HTTP_404_NOT_FOUND
        )
