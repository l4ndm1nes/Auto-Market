from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, EmailVerification, Favorite
from carlisting.models import CarListing, Brand, Location
from celery import current_app
from django.test import override_settings

current_app.conf.task_always_eager = True
current_app.conf.task_eager_propagates = True


class UserTests(APITestCase):

    @override_settings(
        EMAIL_BACKEND='django.core.mail.backends.locmem.EmailBackend',
        CELERY_TASK_ALWAYS_EAGER=True,
        CELERY_TASK_EAGER_PROPAGATES=True
    )
    def setUp(self):
        self.brand = Brand.objects.create(
            name="Toyota",
            country="Japan",
            established_year=1937,
            logo_url="https://example.com/toyota-logo.png",
            description=(
                "Toyota Motor Corporation is a Japanese multinational "
                "automotive manufacturer."
            ),
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
            'users:email_verification',
            kwargs={'code': verification.code}
        )
        self.client.post(verification_url)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

        self.car_listing = CarListing.objects.create(
            user=self.user,
            title="Test Car",
            description="Test Description",
            price=10000.00,
            year=2020,
            mileage=10000,
            engine_type="Gasoline",
            transmission="Manual",
            body_type="Sedan",
            color="Black",
            brand=self.brand,
            location=self.location
        )

        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }, format='json')
        self.access_token = response.data.get('access')

    def test_user_registration(self):
        user = User.objects.get(username=self.user_data['username'])
        self.assertTrue(user.is_active)

    def test_user_login(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_user_profile(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }, format='json')
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')
        response = self.client.get(self.profile_url)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['username'], self.user_data['username'])

    def test_add_to_favorite(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        add_favorite_url = reverse('users:add_to_favorite', args=[self.car_listing.id])

        response = self.client.post(add_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)

        favorites = Favorite.objects.filter(
            user=self.user,
            car_listing=self.car_listing
        )
        self.assertEqual(favorites.count(), 1)

    def test_remove_from_favorite(self):
        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {self.access_token}')
        add_favorite_url = reverse('users:add_to_favorite', args=[self.car_listing.id])
        self.client.post(add_favorite_url)

        remove_favorite_url = reverse(
            'users:remove_from_favorite',
            args=[self.car_listing.id]
        )
        response = self.client.post(remove_favorite_url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        favorites = Favorite.objects.filter(
            user=self.user,
            car_listing=self.car_listing
        )
        self.assertEqual(favorites.count(), 0)

    def test_user_deletion(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }, format='json')
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.delete(
            reverse('users:profile_delete'),
            data={'confirm': True},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.user_data['username'])
