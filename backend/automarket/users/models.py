from django.contrib.auth.models import AbstractUser
from django.db import models
from django.urls import reverse
from django.core.mail import send_mail
from django.utils.timezone import now
from django.conf import settings

from carlisting.models import CarListing


class User(AbstractUser):
    phone_number = models.CharField(max_length=20, blank=True, null=True)
    is_verified = models.BooleanField(default=False)

    def __str__(self):
        return self.username

    class Meta:
        app_label = 'users'
        db_table = 'user'


class EmailVerification(models.Model):
    code = models.UUIDField(unique=True)
    user = models.ForeignKey(to=User, on_delete=models.CASCADE)
    created = models.DateTimeField(auto_now_add=True)
    expiration = models.DateTimeField()

    def __str__(self):
        return f'EmailVerification for {self.user.email}'

    def send_verification_email(self):
        link = reverse('users:email_verification', kwargs={'code': self.code})
        verification_link = f'{settings.DOMAIN_NAME}{link}'
        subject = (
            f'Подтверждение учетной записи для {self.user.username}'
        )
        message = (
            f'Для подтверждения учетной записи для {self.user.email}, '
            f'перейдите по ссылке: {verification_link}'
        )
        send_mail(
            subject,
            message,
            settings.EMAIL_HOST_USER,
            [self.user.email],
            fail_silently=False,
        )

    def is_expired(self):
        return now() >= self.expiration


class Favorite(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='favorites'
    )
    car_listing = models.ForeignKey(
        CarListing,
        on_delete=models.CASCADE,
        related_name='favorited_by'
    )
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ('user', 'car_listing')

    def __str__(self):
        return f'{self.user.username} - {self.car_listing.title}'
