from rest_framework import serializers
from .models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ['registration_id']

    def validate_registration_id(self, value):
        if len(value) < 20:
            raise serializers.ValidationError("توکن FCM معتبر نیست. لطفاً بررسی کنید.")

        # توکن تکراری
        if FCMDevice.objects.filter(registration_id=value).exists():
            raise serializers.ValidationError("این توکن قبلاً ثبت شده است.")

        return value



# -------------------------------------------
#   ثبت شده(notification)  ارسال اعلان به


class FCMNotificationSerializer(serializers.Serializer):
    title = serializers.CharField()
    body = serializers.CharField()
    data = serializers.DictField(required=False)
