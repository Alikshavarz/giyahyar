from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import FCMDevice
from .serializers import FCMDeviceSerializer
from django.conf import settings
from django.utils.translation import gettext_lazy as _

class FCMDeviceCreateUpdateView(generics.CreateAPIView):

    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        """
        این متد قبل از ذخیره کردن شیء فراخوانی می‌شود.
        ما از این متد برای اختصاص کاربر فعلی به توکن و همچنین
        برای به‌روزرسانی توکن در صورت وجود قبلی استفاده می‌کنیم.
        """
        registration_id = serializer.validated_data['registration_id']
        user = self.request.user
        try:

            fcm_device = FCMDevice.objects.get(registration_id=registration_id)
            if fcm_device.user != user:
                fcm_device.user = user
                fcm_device.save()
            serializer.instance = fcm_device
            print(f"FCM token '{registration_id}' updated/already exists for user '{user.username}'.")
        except FCMDevice.DoesNotExist:
            serializer.save(user=user)
            print(f"New FCM token '{registration_id}' registered for user '{user.username}'.")

    def create(self, request, *args, **kwargs):

        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        return Response(
            {'message': _("FCM device token registered/updated successfully."), 'token': serializer.instance.registration_id},
            status=status.HTTP_201_CREATED,
            headers=headers
        )
