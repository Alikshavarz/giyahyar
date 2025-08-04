from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.timezone import now

class CustomUser(AbstractUser):
    phone_number = models.CharField(max_length=15, unique=True)
    is_phone_verified = models.BooleanField(default=False)
    feature_usage_count = models.PositiveIntegerField(default=0)  
    sms_code = models.CharField(max_length=5, blank=True, null=True)
    sms_code_expiry = models.DateTimeField(blank=True, null=True)
    REQUIRED_FIELDS = ['phone_number', 'email']

    def reset_usage_count(self):
        self.feature_usage_count = 0
        self.save()

    @property
    def has_active_subscription(self):
       
        sub = getattr(self, "subscription_set", None)
        if not sub:
            return False
        active_sub = self.subscription_set.filter(is_active=True, expire_at__gte=now()).last()
        return bool(active_sub)
