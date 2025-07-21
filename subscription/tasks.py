from celery import shared_task
from django.utils import timezone
from .models import Subscription
from users.models import CustomUser
from django.core.mail import send_mail

@shared_task
def notify_expiring_subscriptions_3_days():
    check_time = timezone.now() + timezone.timedelta(days=3)
    subs = Subscription.objects.filter(is_active=True, expired_at__date=check_time.date())
    for sub in subs:
        if sub.user.email:
            send_mail(
                subject="یادآوری تمدید اشتراک",
                message="کاربر گرامی، اشتراک شما تا سه روز دیگر به پایان می‌رسد. لطفا جهت تمدید اقدام کنید.",
                from_email="no-reply@myproject.com",
                recipient_list=[sub.user.email]
            )

@shared_task
def deactivate_expired_subscriptions():
    now = timezone.now()
    expired_subs = Subscription.objects.filter(is_active=True, expired_at__lt=now)
    for sub in expired_subs:
        sub.is_active = False
        sub.save()
        
        
        if sub.user.email:
            send_mail(
                subject="اتمام اشتراک",
                message="اشتراک شما به پایان رسیده و دسترسی شما محدود شد.",
                from_email="no-reply@myproject.com",
                recipient_list=[sub.user.email]
            )
