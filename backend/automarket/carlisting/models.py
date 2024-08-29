from django.db import models
from django.conf import settings
from core.models import BaseModel


class Brand(BaseModel):
    name = models.CharField(max_length=255)
    origin_country = models.CharField(max_length=255)
    established_year = models.IntegerField()
    logo_url = models.URLField()
    description = models.TextField()
    website = models.URLField()
    headquarters = models.CharField(max_length=255)

    def __str__(self):
        return self.name


class Location(BaseModel):
    city = models.CharField(max_length=255)
    region = models.CharField(max_length=255)
    country = models.CharField(max_length=255)
    postal_code = models.CharField(max_length=20)
    time_zone = models.CharField(max_length=50)
    description = models.TextField()

    def __str__(self):
        return f'{self.city}, {self.region}, {self.country}'


class CarListing(BaseModel):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True)
    model = models.CharField(max_length=255)
    year = models.IntegerField()
    mileage = models.IntegerField()
    engine_type = models.CharField(max_length=100)
    transmission = models.CharField(max_length=100)
    body_type = models.CharField(max_length=100)
    color = models.CharField(max_length=50)
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True)
    is_sold = models.BooleanField(default=False)
    paid = models.BooleanField(default=False)
    is_hidden = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.title} - {self.user.username}'


class InsuranceInfo(BaseModel):
    car_listing = models.OneToOneField(
        CarListing,
        on_delete=models.CASCADE,
        related_name='insurance_info'
    )
    insurance_start_date = models.DateTimeField()
    insurance_end_date = models.DateTimeField()
    owner_count = models.IntegerField()
    accident_count = models.IntegerField()
    accident_details = models.TextField()

    def __str__(self):
        return f'Insurance Info for {self.car_listing.title}'


class CarImage(BaseModel):
    car_listing = models.ForeignKey(
        CarListing,
        on_delete=models.CASCADE,
        related_name='images'
    )
    image_url = models.URLField()

    def __str__(self):
        return f'Image for {self.car_listing.title} uploaded at {self.created_at}'
