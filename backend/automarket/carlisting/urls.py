from django.urls import path
from .views import (
    CarListingCreateView,
    CarListingDetailView,
    HideCarListingView,
    ShowCarListingView
)

app_name = 'carlisting'

urlpatterns = [
    path('create/', CarListingCreateView.as_view(), name='carlisting_create'),
    path('<int:pk>/', CarListingDetailView.as_view(), name='carlisting_detail'),
    path(
        '<int:car_listing_id>/hide/',
        HideCarListingView.as_view(),
        name='hide_car_listing'
    ),
    path(
        '<int:car_listing_id>/show/',
        ShowCarListingView.as_view(),
        name='show_car_listing'
    ),
]
