from __future__ import absolute_import, unicode_literals
import os
from celery import Celery

# تنظیمات Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'giyahyar.settings')

app = Celery('giyahyar')

# بارگذاری تنظیمات Celery از Django settings
app.config_from_object('django.conf:settings', namespace='CELERY')

# شناسایی تسک‌ها به‌طور خودکار
app.autodiscover_tasks()