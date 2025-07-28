from django.db import models
from django.conf import settings
from django.utils import timezone
from datetime import timedelta
from django.contrib.auth import get_user_model

class SubscriptionPlan(models.Model):
    """مدل پلان‌های اشتراک."""
    name = models.CharField(max_length=50, unique=True)
    duration_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()  # ریال یا تومان
    is_active = models.BooleanField(default=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.name} ({self.duration_days} روز)"

class Subscription(models.Model):
    """مدل وضعیت اشتراک هر کاربر."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='subscriptions')
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)

    def save(self, *args, **kwargs):
        
        if self.is_active:
            Subscription.objects.filter(user=self.user, is_active=True).exclude(pk=self.pk).update(is_active=False)
        super().save(*args, **kwargs)
        self.user.subscription_end = self.expire_at
        self.user.save(update_fields=['subscription_end'])

    def __str__(self):
        return f"{self.user.username} - {self.plan.name} تا {self.expire_at.date()}"

class PaymentHistory(models.Model):
    """مدل تاریخچه پرداخت."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    plan = models.ForeignKey(SubscriptionPlan, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    is_successful = models.BooleanField(default=False)
    pay_time = models.DateTimeField(auto_now_add=True)
    ref_id = models.CharField(max_length=100, null=True, blank=True)  
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} | {self.plan} | {'OK' if self.is_successful else 'FAIL'}"

class Notification(models.Model):
    """مدل آرشیو نوتیفیکیشن - توسعه‌پذیر برای استفاده‌های بعدی."""
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    is_read = models.BooleanField(default=False)

    def __str__(self):
        return f"Notif to {self.user} ({self.created_at.date()})"
    
    
User = get_user_model()    
    
   
