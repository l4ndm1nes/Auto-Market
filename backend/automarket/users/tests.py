from django.core import mail
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase
from users.models import User, EmailVerification
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
        self.user_data = {
            'username': 'testuser',
            'email': 'testuser@example.com',
            'password': 'TestPassword123',
            'first_name': 'Test',
            'last_name': 'User',
            'phone_number': '+1234567890'
        }
        self.login_url = reverse('api:login')
        self.profile_url = reverse('api:profile')

        mail.outbox = []

        self.client.post(reverse('api:register'), self.user_data, format='json')

        self.assertEqual(len(mail.outbox), 1)
        self.assertIn(self.user_data['email'], mail.outbox[0].to)
        self.assertIn('Подтверждение учетной записи', mail.outbox[0].subject)

        user = User.objects.get(username=self.user_data['username'])
        verification = EmailVerification.objects.get(user=user)
        verification_url = reverse('api:email_verification', kwargs={'code': verification.code})
        self.client.post(verification_url)

        user.refresh_from_db()
        self.assertTrue(user.is_verified)

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

    def test_user_deletion(self):
        response = self.client.post(self.login_url, {
            'username': self.user_data['username'],
            'password': self.user_data['password'],
        }, format='json')
        access_token = response.data['access']

        self.client.credentials(HTTP_AUTHORIZATION=f'Bearer {access_token}')

        response = self.client.delete(reverse('api:profile_delete'), data={'confirm': True}, format='json')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)

        with self.assertRaises(User.DoesNotExist):
            User.objects.get(username=self.user_data['username'])
