from rest_framework import serializers
from .models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_id']

    def validate_registration_id(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("توکن FCM معتبر نیست. لطفاً بررسی کنید.")

        return value



# -------------------------------------------
#   ثبت شده(notification)  ارسال اعلان به


class FCMNotificationSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()
    data = serializers.DictField(required=False)
