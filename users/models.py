from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils import timezone
from phonenumber_field.modelfields import PhoneNumberField

class CustomUser(AbstractUser):
   
    phone_number = PhoneNumberField(
        unique=True,
        verbose_name='شماره موبایل',
        blank=False,
        null=False,
        help_text='شماره موبایل کاربر'
    )

    usage_count = models.PositiveIntegerField(
        default=0,
        help_text='تعداد دفعات استفاده غیر اشتراکی'
    )

    subscription_end = models.DateField(
        blank=True,
        null=True,
        help_text='تاریخ پایان اشتراک کاربر'
    )

    def __str__(self):
        return f"{self.username} ({self.phone_number})"

    @property
    def has_active_subscription(self):
        
        return bool(self.subscription_end) and self.subscription_end >= timezone.now().date()

    def increment_usage(self):
       
        if not self.has_active_subscription:
            CustomUser.objects.filter(pk=self.pk).update(usage_count=models.F('usage_count') + 1)
            self.refresh_from_db(fields=['usage_count'])

    def reset_usage(self):
       
        self.usage_count = 0
        self.save(update_fields=['usage_count'])
