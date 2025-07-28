from django.utils import timezone
from .models import Notification

def send_notification(user, message):
   
    print(f"[NOTIF] {user.phone_number or user.username}: {message}")
    Notification.objects.create(user=user, message=message)

def can_extend_subscription(subscription):
   
    days_left = (subscription.expire_at - timezone.now()).days
    return days_left <= 3

def create_notification(user, message):
    Notification.objects.create(user=user, message=message)