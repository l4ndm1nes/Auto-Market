from rest_framework import serializers
from .models import CarListing, Brand, Location, CarImage, InsuranceInfo


class CarListingBriefSerializer(serializers.ModelSerializer):
    first_image_url = serializers.SerializerMethodField()

    class Meta:
        model = CarListing
        fields = ['id', 'title', 'price', 'year', 'mileage', 'first_image_url']

    def get_first_image_url(self, obj):
        first_image = obj.images.first()
        if first_image:
            return first_image.image_url
        return None


class CarImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = CarImage
        fields = ['image_url']


class InsuranceInformationSerializer(serializers.ModelSerializer):
    class Meta:
        model = InsuranceInfo
        fields = [
            'insurance_start_date',
            'insurance_end_date',
            'owner_count',
            'accident_count',
            'accident_details'
        ]


class BrandSerializer(serializers.ModelSerializer):
    class Meta:
        model = Brand
        fields = [
            'name',
            'country',
            'established_year',
            'logo_url',
            'description',
            'website',
            'headquarters'
        ]


class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = [
            'city',
            'region',
            'country',
            'postal_code',
            'time_zone',
            'description'
        ]


class CarListingSerializer(serializers.ModelSerializer):
    brand_name = serializers.CharField(write_only=True)
    location_name = serializers.CharField(write_only=True)
    insurance_information = InsuranceInformationSerializer(source='insurance_info')
    images = CarImageSerializer(many=True)

    class Meta:
        model = CarListing
        fields = [
            'id', 'title', 'description', 'price', 'year', 'mileage',
            'engine_type', 'transmission', 'body_type', 'color',
            'brand_name', 'location_name', 'insurance_information', 'images'
        ]

    def create(self, validated_data):
        brand_name = validated_data.pop('brand_name')
        location_name = validated_data.pop('location_name')

        try:
            brand = Brand.objects.get(name=brand_name)
        except Brand.DoesNotExist:
            raise serializers.ValidationError(
                f"Brand with name '{brand_name}' does not exist."
            )

        try:
            location = Location.objects.get(city=location_name)
        except Location.DoesNotExist:
            raise serializers.ValidationError(
                f"Location with city '{location_name}' does not exist."
            )

        insurance_data = validated_data.pop('insurance_info')
        images_data = validated_data.pop('images')

        car_listing = CarListing.objects.create(
            brand=brand, location=location, **validated_data
        )

        InsuranceInfo.objects.create(
            car_listing=car_listing, **insurance_data
        )

        for image_data in images_data:
            CarImage.objects.create(car_listing=car_listing, **image_data)

        return car_listing

    def update(self, instance, validated_data):
        if 'brand_name' in validated_data:
            brand_name = validated_data.pop('brand_name')
            try:
                brand = Brand.objects.get(name=brand_name)
            except Brand.DoesNotExist:
                raise serializers.ValidationError(
                    f"Brand with name '{brand_name}' does not exist."
                )
            instance.brand = brand

        if 'location_name' in validated_data:
            location_name = validated_data.pop('location_name')
            try:
                location = Location.objects.get(city=location_name)
            except Location.DoesNotExist:
                raise serializers.ValidationError(
                    f"Location with city '{location_name}' does not exist."
                )
            instance.location = location

        if 'insurance_info' in validated_data:
            insurance_data = validated_data.pop('insurance_info')
            insurance_info = instance.insurance_info
            for attr, value in insurance_data.items():
                setattr(insurance_info, attr, value)
            insurance_info.save()

        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        instance.save()

        return instance
