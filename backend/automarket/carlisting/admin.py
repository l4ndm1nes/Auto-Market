from django.contrib import admin
from .models import CarListing, Brand, Location, InsuranceInfo, CarImage


@admin.register(CarListing)
class CarListingAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'pk',
        'user',
        'price',
        'year',
        'brand',
        'location',
        'is_sold',
        'paid'
    )
    search_fields = (
        'title',
        'pk',
        'description',
        'user__username',
        'brand__name',
        'location__city'
    )
    list_filter = ('brand', 'location', 'is_sold', 'paid')
    ordering = ('-created_at',)


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ('name', 'country', 'established_year')
    search_fields = ('name', 'country')
    list_filter = ('country',)
    ordering = ('name',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    list_display = ('city', 'region', 'country')
    search_fields = ('city', 'region', 'country')
    list_filter = ('country',)
    ordering = ('city',)


@admin.register(InsuranceInfo)
class InsuranceInfoAdmin(admin.ModelAdmin):
    list_display = (
        'car_listing',
        'insurance_start_date',
        'insurance_end_date',
        'owner_count',
        'accident_count'
    )
    search_fields = ('car_listing__title',)
    list_filter = ('insurance_start_date', 'insurance_end_date')
    ordering = ('car_listing',)


@admin.register(CarImage)
class CarImageAdmin(admin.ModelAdmin):
    list_display = ('car_listing', 'uploaded_at')
    search_fields = ('car_listing__title',)
    ordering = ('car_listing', 'uploaded_at')
