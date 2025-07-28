from django.utils import timezone
from .models import Subscription, Notification

def check_expiring_subscriptions():
    now = timezone.now()
    three_days_later = now + timezone.timedelta(days=3)
    subscriptions = Subscription.objects.filter(is_active=True, expire_at__gte=now, expire_at__lte=three_days_later)
    for sub in subscriptions:
        msg = f"اشتراک شما تا {sub.expire_at.date()} فعال است. فقط ۳ روز دیگر باقیست! برای تمدید اقدام کنید."
        Notification.objects.get_or_create(user=sub.user, message=msg)

    expired = Subscription.objects.filter(is_active=True, expire_at__lt=now)
    for sub in expired:
        sub.is_active = False
        sub.save()
        msg = "اشتراک شما به پایان رسید و دسترسی محدود شد. برای فعالسازی مجدد، اشتراک جدید خریداری کنید."
        Notification.objects.get_or_create(user=sub.user, message=msg)