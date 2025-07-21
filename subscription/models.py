from django.db import models
from django.conf import settings
from django.utils import timezone

class Plan(models.Model):
    name = models.CharField(max_length=50, unique=True)
    description = models.TextField(blank=True)
    duration_days = models.PositiveIntegerField()
    price = models.PositiveIntegerField()
    is_active = models.BooleanField(default=True)

    def __str__(self):
        return self.name

class Subscription(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name="subscriptions")
    plan = models.ForeignKey(Plan, on_delete=models.PROTECT)
    started_at = models.DateTimeField(default=timezone.now)
    expired_at = models.DateTimeField()
    is_active = models.BooleanField(default=True)
    auto_renew = models.BooleanField(default=False)

    def __str__(self):
        return f"{self.user.username} - {self.plan.name}"

class PaymentHistory(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    subscription = models.ForeignKey(Subscription, null=True, blank=True, on_delete=models.SET_NULL)
    amount = models.PositiveIntegerField()
    plan_name = models.CharField(max_length=50)
    pay_time = models.DateTimeField(auto_now_add=True)
    status = models.CharField(
        max_length=20, choices=[('pending','در انتظار'),('success','موفق'),('failed','ناموفق')]
    )
    payment_gateway = models.CharField(max_length=32, blank=True)
    ref_id = models.CharField(max_length=40, blank=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} | {self.amount} | {self.status}"
