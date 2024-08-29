from celery import shared_task
from .models import EmailVerification


@shared_task
def send_verification_email_task(user_id, code, email):
    try:
        verification = EmailVerification.objects.get(user_id=user_id, code=code)
        verification.send_verification_email()
    except EmailVerification.DoesNotExist:
        return False
    return True
