from rest_framework import generics, status
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.pagination import PageNumberPagination
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import CarListing
from .serializers import CarListingSerializer, CarListingBriefSerializer


class CarListingListView(generics.ListAPIView):
    queryset = CarListing.objects.all()
    serializer_class = CarListingBriefSerializer
    pagination_class = PageNumberPagination

    def get_queryset(self):
        return CarListing.objects.filter(is_hidden=False).order_by('-created_at')


class CarListingCreateView(generics.ListCreateAPIView):
    queryset = CarListing.objects.all()
    serializer_class = CarListingSerializer

    def get_permissions(self):
        if self.request.method == 'POST':
            return [IsAuthenticated()]
        return []

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class CarListingDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = CarListing.objects.all()
    serializer_class = CarListingSerializer
    permission_classes = [IsAuthenticated]

    def perform_update(self, serializer):
        if self.get_object().user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to edit this listing."
            )
        serializer.save()

    def perform_destroy(self, instance):
        confirm = self.request.query_params.get('confirm')
        if confirm != 'True':
            raise PermissionDenied(
                "Please provide confirm=True to delete this listing."
            )
        if instance.user != self.request.user:
            raise PermissionDenied(
                "You do not have permission to delete this listing."
            )
        instance.delete()


class HideCarListingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_listing_id):
        try:
            car_listing = CarListing.objects.get(
                id=car_listing_id, user=request.user
            )
        except CarListing.DoesNotExist:
            return Response(
                {"detail": "Car listing not found or you do not have "
                           "permission to hide it."},
                status=status.HTTP_404_NOT_FOUND
            )

        car_listing.is_hidden = True
        car_listing.save()
        return Response(
            {"detail": "Car listing is now hidden."},
            status=status.HTTP_200_OK
        )


class ShowCarListingView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, car_listing_id):
        try:
            car_listing = CarListing.objects.get(
                id=car_listing_id, user=request.user
            )
        except CarListing.DoesNotExist:
            return Response(
                {"detail": "Car listing not found or you do not have "
                           "permission to show it."},
                status=status.HTTP_404_NOT_FOUND
            )

        car_listing.is_hidden = False
        car_listing.save()
        return Response(
            {"detail": "Car listing is now visible."},
            status=status.HTTP_200_OK
        )
