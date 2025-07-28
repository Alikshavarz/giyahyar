from django.utils import timezone
from .models import Subscription, Notification

def send_subscription_reminders():
    ''' پیدا کردن اشتراک‌هایی که ۳ روز مونده به پایانشون  '''
    now = timezone.now()
    almost_expire = now + timezone.timedelta(days=3)
    qs = Subscription.objects.filter(is_active=True, expire_at__date=almost_expire.date())
    for sub in qs:
        message = f"اشتراک شما در پلن {sub.plan.name} تا ۳ روز دیگر به پایان می‌رسد. لطفاً تمدید کنید."
        if not Notification.objects.filter(user=sub.user, message__contains=sub.plan.name, created_at__date=now.date()).exists():
            Notification.objects.create(user=sub.user, message=message)
    expired = Subscription.objects.filter(is_active=True, expire_at__lt=now)
    for sub in expired:
        sub.is_active = False
        sub.save()
        Notification.objects.create(user=sub.user, message=f"اشتراک شما در پلن {sub.plan.name} به پایان رسید و دسترسی شما محدود شد.")
