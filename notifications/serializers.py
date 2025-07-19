from rest_framework import serializers
from .models import FCMDevice # مدل FCMDevice رو ایمپورت می‌کنیم

class FCMDeviceSerializer(serializers.ModelSerializer):
    """
    سریالایزر برای مدل FCMDevice.
    این سریالایزر برای ثبت (register) توکن‌های FCM دستگاه‌ها استفاده می‌شود.
    """
    class Meta:
        model = FCMDevice
        fields = ['registration_id'] # فقط فیلد registration_id رو برای ثبت نیاز داریم
        # فیلد 'user' به صورت خودکار در perform_create در View تنظیم می‌شود.