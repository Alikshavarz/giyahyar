from celery import shared_task
from django.utils import timezone
from .models import Subscription


try:
    from notifications.models import FCMDevice
except ImportError:
    FCMDevice = None

def send_fcm_notification(user, title, message):
    if FCMDevice:
        devices = FCMDevice.objects.filter(user=user, active=True)
        if devices:
            devices.send_message(title=title, body=message)
 
    else:
        print(f"FAKE FCM: {user} | {title}: {message}")

@shared_task
def notify_expiry_soon():
    """
    به کاربرانی که 3 روز تا پایان اشتراک‌شان مانده نوتیف بده.
    """
    target = timezone.now() + timezone.timedelta(days=3)
    subs = Subscription.objects.filter(is_active=True, expired_at__date=target.date())
    for sub in subs:
        send_fcm(
            sub.user,
            "یادآوری تمدید اشتراک",
            f"اشتراک شما تا {sub.expired_at.date()} اعتبار دارد."
        )

@shared_task
def deactivate_expired():
    """
    اشتراک‌های منقضی را غیرفعال کن و نوتیف بده.
    """
    now = timezone.now()
    expireds = Subscription.objects.filter(is_active=True, expired_at__lt=now)
    for sub in expireds:
        sub.is_active = False
        sub.save(update_fields=['is_active'])
        send_fcm(sub.user, "اتمام اشتراک", "اشتراک شما به پایان رسید.")

