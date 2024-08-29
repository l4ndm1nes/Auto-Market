from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, EmailVerification
from carlisting.models import CarListing, Brand, Location
from celery import current_app
from django.test import override_settings

current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True


class CarListingTests(APITestCase):

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True
    )
    def setUp(self):
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
        self.login_url = reverse('users:login')
        self.profile_url = reverse('users:profile')

        mail.outbox = []

        self.client.post(reverse('users:register'), self.user_data, format='json')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user_data['email'], mail.outbox[0].to)
        self.assertIn('Подтверждение учетной записи', mail.outbox[0].subject)

        user = User.objects.get(username=self.user_data['username'])
        self.user = user

        verification = EmailVerification.objects.get(user=user)
        verification_url = reverse(
            'users:email_verification', kwargs={'code': verification.code}
        )
        self.client.post(verification_url)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        self.brand = Brand.objects.create(
            name="Toyota",
            country="Japan",
            established_year=1937,
            logo_url="https://example.com/toyota-logo.png",
            description="Toyota Motor Corporation is a Japanese multinational "
                        "automotive manufacturer.",
            website="https://www.toyota.com",
            headquarters="Toyota City, Aichi Prefecture, Japan"
        )

        self.location = Location.objects.create(
            city="Kyiv",
            region="Kyiv Oblast",
            country="Ukraine",
            postal_code="01001",
            time_zone="Europe/Kyiv",
            description="The capital city of Ukraine."
        )

        response = self.client.post(
            self.login_url,
            {'username': self.user_data['username'],
             'password': self.user_data['password']},
            format='json'
        )
        self.access_token = response.data.get('access')

        self.car_listing_data = {
            'id': 1,
            'title': 'Test Car',
            'description': 'Test Description',
            'price': 10000.00,
            'year': 2020,
            'mileage': 10000,
            'engine_type': 'Gasoline',
            'transmission': 'Manual',
            'body_type': 'Sedan',
            'color': 'Black',
            'brand_name': 'Toyota',
            'location_name': 'Kyiv',
            'insurance_information': {
                'insurance_start_date': '2024-01-01',
                'insurance_end_date': '2025-01-01',
                'owner_count': 1,
                'accident_count': 0,
                'accident_details': 'No accidents'
            },
            'images': [
                {'image_url': 'http://example.com/image1.jpg'},
                {'image_url': 'http://example.com/image2.jpg'}
            ]
        }

    def test_create_car_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            reverse('carlisting:carlisting_create'),
            self.car_listing_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(CarListing.objects.count(), 1)

    def test_update_car_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            reverse('carlisting:carlisting_create'),
            self.car_listing_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        car_listing_id = response.data['id']

        update_data = {'mileage': 15000}
        response = self.client.patch(
            reverse('carlisting:carlisting_detail', args=[car_listing_id]),
            update_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(CarListing.objects.get(id=car_listing_id).mileage, 15000)

    def test_hide_car_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            reverse('carlisting:carlisting_create'),
            self.car_listing_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        car_listing_id = response.data['id']

        hide_url = reverse('carlisting:hide_car_listing', args=[car_listing_id])
        response = self.client.post(hide_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertTrue(CarListing.objects.get(id=car_listing_id).is_hidden)

    def test_show_car_listing(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        response = self.client.post(
            reverse('carlisting:carlisting_create'),
            self.car_listing_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertIn('id', response.data)
        car_listing_id = response.data['id']

        CarListing.objects.filter(id=car_listing_id).update(is_hidden=True)

        show_url = reverse('carlisting:show_car_listing', args=[car_listing_id])
        response = self.client.post(show_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertFalse(CarListing.objects.get(id=car_listing_id).is_hidden)
