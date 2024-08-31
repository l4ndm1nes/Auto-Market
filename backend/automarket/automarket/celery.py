from __future__ import absolute_import, unicode_literals
import os
from celery import Celery
import logging


os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'automarket.settings')

app = Celery('automarket')

app.config_from_object('django.conf:settings', namespace='CELERY')

app.autodiscover_tasks()

logger = logging.getLogger(__name__)


@app.task(bind=True)
def debug_task(self):
    logger.info(f'Request: {self.request!r}')
