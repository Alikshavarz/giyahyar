from django.db.models.signals import post_save, post_delete
from django.dispatch import receiver
from .models import Subscription
from users.models import CustomUser  

@receiver([post_save, post_delete], sender=Subscription)
def sync_subscription_end_with_user(sender, instance, **kwargs):
    # پیدا کردن آخرین اشتراک فعال
    user = instance.user
    active_sub = Subscription.objects.filter(
        user=user, is_active=True, expired_at__gte=timezone.now()
    ).order_by('-expired_at').first()
    user.subscription_end = active_sub.expired_at if active_sub else None
    user.save(update_fields=["subscription_end"])
