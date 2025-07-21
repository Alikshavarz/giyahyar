from django.db import models
from django.conf import settings
from django.utils import timezone
from django.utils.translation import gettext_lazy as _

class Plan(models.Model):

    DURATION_CHOICES = [
        (30, _("یک ماهه")),
        (90, _("سه ماهه")),

    ]
    name = models.CharField(max_length=64, unique=True)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField(choices=DURATION_CHOICES)
    price = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return f"{self.name} ({self.duration_days} روز)"

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT, related_name="subscriptions")
    started_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)
    last_payment_status = models.CharField(max_length=16, default='pending', choices=[
        ("pending", "در انتظار"), ("success", "موفق"), ("failed", "ناموفق"),
    ])

    def __str__(self):
        return f"{self.user.username} | {self.plan.name} | {'فعال' if self.is_active else 'غیرفعال'}"

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, on_delete=models.SET_NULL, null=True)
    amount = models.PositiveIntegerField()
    plan_name = models.CharField(max_length=64)
    pay_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=16, choices=[
        ("pending", "در انتظار"), ("success", "موفق"), ("failed", "ناموفق")
    ])
    payment_gateway = models.CharField(max_length=64, blank=True, null=True)
    ref_id = models.CharField(max_length=64, blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user.username} | {self.plan_name} | {self.amount} | {self.status}"
