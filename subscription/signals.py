from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Subscription
from users.models import CustomUser
from django.utils import timezone

@receiver([post_save, post_delete], sender=Subscription)
def sync_subscription_end(sender, instance, **kwargs):
    user = instance.user
    latest_active = Subscription.objects.filter(user=user, is_active=True, expired_at__gt=timezone.now())\
                      .order_by('-expired_at').first()
    user.subscription_end = latest_active.expired_at if latest_active else None
    user.save(update_fields=['subscription_end'])
